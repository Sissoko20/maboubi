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
    txt_content = uploaded_file.read().decode("utf-8", errors="ignore")
    df = parse_ubipharm_txt(txt_content)

    if df.empty:
        st.warning("Le parsing n’a retourné aucune ligne. Vérifiez le format du fichier TXT.")
    else:
        st.success("✅ Fichier parsé avec succès")

        # Vue globale
        st.subheader("🌍 Vue globale : tous les produits")
        st.dataframe(df, use_container_width=True)

        # Choix du mode de répartition
        repartition_mode = st.radio(
            "Choisissez le mode de répartition par communes",
            options=["Verticale (lignes)", "Horizontale (colonnes)"],
            index=1  # par défaut horizontale
        )

        regions = df["Région"].dropna().unique()
        repartition_results = {}

        for region in regions:
            st.markdown(f"### 📍 {region}")
            region_df = df[df["Région"] == region]

            if region in region_to_communes:
                communes = region_to_communes[region]

                if repartition_mode == "Verticale (lignes)":
                    df_communes = repartir_par_communes(region_df, communes, col="11/25")
                else:
                    df_communes = repartir_par_communes_horizontal(region_df, communes, col="11/25")

                # ➕ Sélecteur de colonnes appliqué à la répartition
                st.subheader(f"🧩 Filtrage des colonnes pour {region}")
                selected_cols = st.multiselect(
                    f"Colonnes à garder ({region})",
                    options=df_communes.columns.tolist(),
                    default=df_communes.columns.tolist(),
                    key=f"filter_{region}"  # clé unique par région
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
