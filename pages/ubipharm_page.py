import streamlit as st
import pandas as pd
from io import BytesIO

from parsers.ubipharm import parse_ubipharm_txt
from components.repartition import (
    repartir_par_communes,
    repartir_par_communes_horizontal,
    region_to_communes
)


st.header("⚙️ Refactoring des données - Ubipharm")

uploaded_file = st.file_uploader("Upload fichier TXT brut (Ubipharm)", type="txt")

if uploaded_file:
    # Lecture brute en bytes
    raw_bytes = uploaded_file.read()

    # Essai multi-encodages pour éviter blocages liés au nom ou BOM
    for enc in ["utf-8-sig", "latin-1", "utf-8"]:
        try:
            txt_content = raw_bytes.decode(enc)
            break
        except UnicodeDecodeError:
            txt_content = None

    if txt_content is None:
        st.error("❌ Impossible de décoder le fichier. Vérifiez l'encodage.")
    else:
        # Nettoyage BOM éventuel
        txt_content = txt_content.replace("\ufeff", "")

        # Parsing basé uniquement sur le contenu
        df = parse_ubipharm_txt(txt_content)

        if df.empty:
            st.warning("⚠️ Le parsing n’a retourné aucune ligne. Vérifiez le format du fichier TXT.")
        else:
            st.success("✅ Fichier parsé avec succès")
            st.dataframe(df.head())  # aperçu des données

        # Vue globale
        st.subheader("🌍 Vue globale : tous les produits")
        st.dataframe(df, use_container_width=True)

        # Suppression des produits indésirables
        st.subheader("🧹 Nettoyage : supprimer les produits non désirables")

        product_col = "Produit" if "Produit" in df.columns else "Nom Produit"
        undesirable_products = st.multiselect(
            "Sélectionnez les produits à supprimer :",
            options=df[product_col].unique()
        )

        # Filtrage
        if undesirable_products:
            df_filtered = df[~df[product_col].isin(undesirable_products)]
            st.success(f"✅ {len(undesirable_products)} produit(s) supprimé(s)")
            st.dataframe(df_filtered, use_container_width=True)
        else:
            df_filtered = df.copy()
            st.info("ℹ️ Aucun produit supprimé")

        # Colonnes dynamiques (toutes les colonnes de ventes)
        sales_cols = [c for c in df_filtered.columns if c not in ["Région", "Code Produit", "Nom Produit", "Stock", "CR"]]

        # Sélecteur Streamlit pour choisir la colonne de ventes
        selected_sales_col = st.selectbox(
            "📊 Choisissez la colonne de ventes à utiliser pour la répartition",
            options=sales_cols,
            index=0
        )

        # Choix du mode de répartition
        repartition_mode = st.radio(
            "Choisissez le mode de répartition par communes",
            options=["Verticale (lignes)", "Horizontale (colonnes)"],
            index=1
        )

        regions = df_filtered["Région"].dropna().unique()
        repartition_results = {}

        for region in regions:
            st.markdown(f"### 📍 {region}")
            region_df = df_filtered[df_filtered["Région"] == region]

            if region in region_to_communes:
                communes = region_to_communes[region]

                if repartition_mode == "Verticale (lignes)":
                    df_communes = repartir_par_communes(region_df, communes, col=selected_sales_col)
                else:
                    df_communes = repartir_par_communes_horizontal(region_df, communes, col=selected_sales_col)

                # ➕ Sélecteur de colonnes appliqué à la répartition
                st.subheader(f"🧩 Filtrage des colonnes pour {region}")
                selected_cols = st.multiselect(
                    f"Colonnes à garder ({region})",
                    options=df_communes.columns.tolist(),
                    default=df_communes.columns.tolist(),
                    key=f"filter_{region}"
                )

                filtered_communes = df_communes[selected_cols]
                st.dataframe(filtered_communes, use_container_width=True)

                repartition_results[region] = filtered_communes

        # Export Excel basé sur la répartition filtrée
        if st.button("📥 Télécharger Excel (répartition filtrée)"):
            output = BytesIO()
            with pd.ExcelWriter(output, engine="openpyxl") as writer:
                sheet_names = {}
                for region, df_communes in repartition_results.items():
                    sheet_name = region[:31]
                    if sheet_name in sheet_names:
                        sheet_names[sheet_name] += 1
                        sheet_name = f"{sheet_name}_{sheet_names[sheet_name]}"
                    else:
                        sheet_names[sheet_name] = 1
                    df_communes.to_excel(writer, index=False, sheet_name=sheet_name)
            excel_data = output.getvalue()

            st.download_button(
                label="📥 Télécharger Excel (répartition filtrée par communes)",
                data=excel_data,
                file_name="ventes_reparties_filtrees.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
