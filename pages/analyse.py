import re
import io
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Analyse Ubipharm", layout="wide")

st.header("📊 Analyse des indicateurs de performance — Ubipharm")

uploaded = st.file_uploader("Chargez un fichier CSV exporté (répartition par communes)", type=["csv"])

def detect_month_column(df: pd.DataFrame):
    """Retourne la colonne du mois courant (NN/NN) si trouvée, sinon None."""
    month_re = re.compile(r"^\d{2}/\d{2}$")
    for col in df.columns:
        if month_re.match(str(col).strip()):
            return col
    return None

def detect_commune_columns(df: pd.DataFrame, month_col: str):
    """Retourne les colonnes communes liées au mois courant: '<mois> Commune X'."""
    if not month_col:
        return []
    pattern = re.compile(rf"^{re.escape(month_col)}\s+Commune\s+\d+$")
    return [c for c in df.columns if pattern.match(str(c))]

def kpi_block(df: pd.DataFrame, month_col: str):
    total_month = df[month_col].sum() if month_col in df.columns else 0
    nb_products = df.shape[0]
    avg_per_product = total_month / nb_products if nb_products else 0

    c1, c2, c3 = st.columns(3)
    c1.metric("Total ventes (mois courant)", f"{total_month:,.0f}")
    c2.metric("Nombre de produits", f"{nb_products}")
    c3.metric("Vente moyenne / produit", f"{avg_per_product:,.2f}")

def top_bottom_products(df: pd.DataFrame, month_col: str, n=10):
    st.subheader("🏆 Top produits (mois courant)")
    top_df = df.sort_values(by=month_col, ascending=False).head(n)
    st.dataframe(top_df[["Région", "Nom Produit", month_col]], use_container_width=True)

    st.subheader("🔻 Produits à faible consommation")
    bottom_df = df.sort_values(by=month_col, ascending=True).head(n)
    st.dataframe(bottom_df[["Région", "Nom Produit", month_col]], use_container_width=True)

def commune_comparison(df: pd.DataFrame, month_col: str, commune_cols: list):
    if not commune_cols:
        st.info("Aucune colonne de communes détectée pour le mois courant.")
        return
    st.subheader("🏙️ Répartition par communes (mois courant)")
    # Sommes par commune
    sums = df[commune_cols].sum().rename("Ventes")
    st.bar_chart(sums)

    # Tableau détaillé
    st.dataframe(df[["Région", "Nom Produit"] + commune_cols + [month_col]], use_container_width=True)

def stock_cr_section(df: pd.DataFrame):
    cols = [c for c in ["Stock", "CR"] if c in df.columns]
    if not cols:
        return
    st.subheader("📦 Stock & CR")
    c1, c2 = st.columns(2)
    if "Stock" in cols:
        c1.metric("Stock total", f"{df['Stock'].fillna(0).sum():,.0f}")
    if "CR" in cols:
        c2.metric("CR total", f"{df['CR'].fillna(0).sum():,.0f}")
    st.dataframe(df[["Région", "Nom Produit"] + cols], use_container_width=True)

def export_section(df: pd.DataFrame):
    st.subheader("📥 Export")
    csv_bytes = df.to_csv(index=False).encode("utf-8")
    st.download_button("Télécharger CSV (filtré)", csv_bytes, "analyse_filtrée.csv", "text/csv")

    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Analyse")
    st.download_button(
        "Télécharger Excel (filtré)",
        output.getvalue(),
        "analyse_filtrée.xlsx",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

if uploaded:
    df = pd.read_csv(uploaded)
    # Détection du mois courant
    month_col = detect_month_column(df)
    if not month_col:
        st.error("Impossible de détecter la colonne du mois courant (format NN/NN). Vérifiez votre export.")
        st.dataframe(df.head(), use_container_width=True)
        st.stop()

    st.success(f"Mois courant détecté: {month_col}")

    # Filtres
    st.sidebar.header("🎛️ Filtres")
    regions = sorted(df["Région"].dropna().unique()) if "Région" in df.columns else []
    selected_regions = st.sidebar.multiselect("Régions", options=regions, default=regions)
    search = st.sidebar.text_input("Recherche produit (contient)")

    filtered = df.copy()
    if selected_regions and "Région" in filtered.columns:
        filtered = filtered[filtered["Région"].isin(selected_regions)]
    if search:
        filtered = filtered[filtered["Nom Produit"].str.contains(search, case=False, na=False)]

    # KPIs
    kpi_block(filtered, month_col)

    # Graphique global des ventes par produit
    st.subheader("📈 Ventes par produit (mois courant)")
    chart_df = filtered[["Nom Produit", month_col]].sort_values(by=month_col, ascending=False).head(30)
    st.bar_chart(chart_df.set_index("Nom Produit"))

    # Top / Bottom
    top_bottom_products(filtered, month_col, n=10)

    # Communes
    commune_cols = detect_commune_columns(filtered, month_col)
    commune_comparison(filtered, month_col, commune_cols)

    # Stock / CR
    stock_cr_section(filtered)

    # Tableau complet filtré
    st.subheader("🧾 Tableau filtré")
    st.dataframe(filtered, use_container_width=True)

    # Export
    export_section(filtered)
else:
    st.info("Chargez un CSV exporté pour lancer l’analyse.")
