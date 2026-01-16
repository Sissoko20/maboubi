import streamlit as st
import pandas as pd
from io import BytesIO

from parsers.ubipharm import parse_ubipharm_txt

st.header("⚙️ Refactoring des données - Ubipharm")

uploaded_file = st.file_uploader("Upload fichier TXT brut (Ubipharm)", type="txt")

if uploaded_file:
    # Lecture brute en bytes
    raw_bytes = uploaded_file.read()

    # Essai multi-encodages
    txt_content = None
    for enc in ["utf-8-sig", "latin-1", "utf-8"]:
        try:
            txt_content = raw_bytes.decode(enc)
            break
        except UnicodeDecodeError:
            continue

    if txt_content is None:
        st.error("❌ Impossible de décoder le fichier. Vérifiez l'encodage.")
    else:
        # Nettoyage BOM éventuel
        txt_content = txt_content.replace("\ufeff", "")

        # Parsing
        df = parse_ubipharm_txt(txt_content)

        if df.empty:
            st.warning("⚠️ Le parsing n’a retourné aucune ligne. Vérifiez le format du fichier TXT.")
        else:
            st.success("✅ Fichier parsé avec succès")
            st.dataframe(df.head())

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
        else:
            df_filtered = df.copy()
            st.info("ℹ️ Aucun produit supprimé")

    # Vue globale
st.subheader("🌍 Vue globale : tous les produits")

# Colonnes de ventes (exclure les colonnes fixes)
sales_cols = [c for c in df_filtered.columns if c.startswith("M-") or "/" in c or c == "MOIS"]

# Case à cocher pour tout afficher
show_all = st.checkbox("Tout afficher les colonnes de ventes")

if show_all:
    selected_cols = sales_cols
else:
    # Choix manuel des colonnes
    selected_cols = st.multiselect(
        "Choisissez les colonnes de ventes à afficher :",
        options=sales_cols,
        default=["11/25"]  # par défaut uniquement 11/25
    )

# Colonnes fixes toujours visibles
fixed_cols = ["Région", "Nom Produit"]

# Construire le DataFrame filtré pour l’affichage
cols_to_show = fixed_cols + selected_cols
st.dataframe(df_filtered[cols_to_show], use_container_width=True)

# Étape export : génération en cours puis téléchargement
if st.button("📥 Générer Excel (par région)"):
    st.info("⏳ Génération en cours...")

    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        sheet_names = {}
        # ⚠️ Utiliser df_filtered et limiter aux colonnes choisies
        for region, df_region in df_filtered.groupby("Région"):
            sheet_name = region[:31]  # Excel limite à 31 caractères
            if sheet_name in sheet_names:
                sheet_names[sheet_name] += 1
                sheet_name = f"{sheet_name}_{sheet_names[sheet_name]}"
            else:
                sheet_names[sheet_name] = 1
            # Exporter uniquement les colonnes sélectionnées
            df_region[cols_to_show].to_excel(writer, index=False, sheet_name=sheet_name)

    excel_data = output.getvalue()

    st.success("✅ Fichier généré avec succès !")
    st.download_button(
        label="📥 Télécharger Excel (par région)",
        data=excel_data,
        file_name="ventes_par_region.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
