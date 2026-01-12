import streamlit as st
import pandas as pd
import re
from io import BytesIO


# --- Page Refactoring ---
st.header("⚙️ Refactoring des données")
uploaded_file = st.file_uploader("Upload fichier TXT brut", type="txt")

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

        # Vue par région
        st.subheader("📋 Produits regroupés par région")
        regions = df["Région"].dropna().unique()
        for region in regions:
            st.markdown(f"### 📍 {region}")
            region_df = df[df["Région"] == region]
            st.dataframe(region_df, use_container_width=True)

        # Sélecteur de colonnes pour export
        st.subheader("🧩 Sélection des colonnes à exporter")
        selected_cols = st.multiselect(
            "Choisissez les colonnes à garder",
            options=df.columns.tolist(),
            default=df.columns.tolist()
        )

        if st.button("Appliquer le filtrage"):
            filtered_df = df[selected_cols]
            st.subheader("🗂️ Aperçu des colonnes sélectionnées (vue globale)")
            st.dataframe(filtered_df, use_container_width=True)

            

            # Export Excel uniquement par région
            output = BytesIO()
            with pd.ExcelWriter(output, engine="openpyxl") as writer:
                for region in regions:
                    region_df = filtered_df[filtered_df["Région"] == region]
                    region_df.to_excel(writer, index=False, sheet_name=region[:31])
            excel_data = output.getvalue()

            st.download_button(
                label="📥 Télécharger Excel (par région uniquement)",
                data=excel_data,
                file_name="ventes_par_region.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
