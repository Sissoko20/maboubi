import streamlit as st
import pandas as pd
from io import BytesIO

from parsers.ubipharm import parse_ubipharm_txt

# --------------------------------------------------
# CONFIG
# --------------------------------------------------
st.set_page_config(page_title="Ubipharm - Refactoring & Analyse", layout="wide")
st.header("⚙️ Refactoring des données - Ubipharm")

# --------------------------------------------------
# INIT
# --------------------------------------------------
df_filtered = None
product_col = None
selected_cols = []

# --------------------------------------------------
# UPLOAD
# --------------------------------------------------
uploaded_file = st.file_uploader("📂 Upload fichier TXT brut (Ubipharm)", type="txt")

if uploaded_file:
    raw_bytes = uploaded_file.read()

    # Multi-encodages
    txt_content = None
    for enc in ["utf-8-sig", "latin-1", "utf-8"]:
        try:
            txt_content = raw_bytes.decode(enc)
            break
        except UnicodeDecodeError:
            continue

    if txt_content is None:
        st.error("❌ Impossible de décoder le fichier TXT.")
    else:
        txt_content = txt_content.replace("\ufeff", "")

        # Parsing
        df = parse_ubipharm_txt(txt_content)

        if df.empty:
            st.warning("⚠️ Le parsing n’a retourné aucune donnée.")
        else:
            st.success("✅ Fichier parsé avec succès")
            st.dataframe(df.head(), use_container_width=True)

            # --------------------------------------------------
            # NETTOYAGE PRODUITS
            # --------------------------------------------------
            product_col = "Produit" if "Produit" in df.columns else "Nom Produit"

            st.subheader("🧹 Nettoyage : suppression de produits")
            undesirable_products = st.multiselect(
                "Sélectionnez les produits à supprimer :",
                options=sorted(df[product_col].unique())
            )

            if undesirable_products:
                df_filtered = df[~df[product_col].isin(undesirable_products)]
                st.success(f"✅ {len(undesirable_products)} produit(s) supprimé(s)")
            else:
                df_filtered = df.copy()
                st.info("ℹ️ Aucun produit supprimé")

# --------------------------------------------------
# VUE GLOBALE
# --------------------------------------------------
if df_filtered is not None:

    st.divider()
    st.subheader("🌍 Vue globale : données filtrées")

    # Colonnes ventes
    sales_cols = [
        c for c in df_filtered.columns
        if c.startswith("M-") or "/" in c or c == "MOIS"
    ]

    show_all = st.checkbox("📊 Afficher toutes les colonnes de ventes")

    if show_all:
        selected_cols = sales_cols
    else:
        default_col = sales_cols[0] if sales_cols else None
        selected_cols = st.multiselect(
            "Choisissez les colonnes de ventes à afficher :",
            options=sales_cols,
            default=[default_col] if default_col else []
        )

    fixed_cols = ["Région", product_col]
    cols_to_show = fixed_cols + selected_cols

    st.dataframe(df_filtered[cols_to_show], use_container_width=True)

    # --------------------------------------------------
    # EXPORT EXCEL
    # --------------------------------------------------
    st.divider()
    if st.button("📥 Générer Excel (par région)"):

        output = BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            sheet_names = {}

            for region, df_region in df_filtered.groupby("Région"):
                sheet_name = region[:31]
                if sheet_name in sheet_names:
                    sheet_names[sheet_name] += 1
                    sheet_name = f"{sheet_name}_{sheet_names[sheet_name]}"
                else:
                    sheet_names[sheet_name] = 1

                df_region[cols_to_show].to_excel(
                    writer,
                    index=False,
                    sheet_name=sheet_name
                )

        excel_data = output.getvalue()

        st.success("✅ Fichier Excel généré")
        st.download_button(
            label="📥 Télécharger Excel (par région)",
            data=excel_data,
            file_name="ventes_par_region.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

        # --------------------------------------------------
        # ANALYSES
        # --------------------------------------------------
        st.divider()
        st.subheader("📊 Analyses – Données filtrées")

        sales_numeric = df_filtered[selected_cols].apply(
            pd.to_numeric, errors="coerce"
        )

        # KPI
        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("💰 Ventes totales", f"{sales_numeric.sum().sum():,.0f}")

        with col2:
            st.metric("📦 Produits", df_filtered[product_col].nunique())

        with col3:
            st.metric("🌍 Régions", df_filtered["Région"].nunique())

        # Classement régions
        st.subheader("🏆 Classement des régions")

        region_sales = (
            df_filtered
            .assign(Total=sales_numeric.sum(axis=1))
            .groupby("Région")["Total"]
            .sum()
            .sort_values(ascending=False)
        )

        st.dataframe(region_sales.reset_index(), use_container_width=True)

        # Top produits
        st.subheader("🔥 Top 10 produits")

        top_products = (
            df_filtered
            .assign(Total=sales_numeric.sum(axis=1))
            .groupby(product_col)["Total"]
            .sum()
            .sort_values(ascending=False)
            .head(10)
        )

        st.dataframe(top_products.reset_index(), use_container_width=True)

        # Faible consommation
        st.subheader("⚠️ Produits à faible consommation")

        threshold = st.number_input(
            "Seuil de vente",
            min_value=0,
            value=10
        )

        low_products = (
            df_filtered
            .assign(Total=sales_numeric.sum(axis=1))
            .groupby(product_col)["Total"]
            .sum()
            .reset_index()
        )

        low_products = low_products[low_products["Total"] <= threshold]
        st.dataframe(low_products, use_container_width=True)

