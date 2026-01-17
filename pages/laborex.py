import streamlit as st
import pandas as pd
from io import BytesIO
from streamlit_option_menu import option_menu

st.set_page_config(page_title="Tableau de bord", page_icon="📊", layout="wide")


st.title("MABOU BI ")
st.write("Bienvenue dans votre application d'analyse de données.")



# -------------------------------
# Barre de navigation moderne
# -------------------------------
with st.sidebar:
    st.image("assets/logo.png", width=120)
    selected = option_menu(
        "Navigation",
        ["🏠 Tableau de bord", "📊 Extraction Ubipharm", "🧾 Extraction Laborex", ],
        icons=["house", "bar-chart", "file-text"],
        menu_icon="cast",
        default_index=0,
    )

# -------------------------------
# Logique de navigation
# -------------------------------
if selected == "🏠 Tableau de bord":
   

    st.subheader("⚙️ Actions rapides")
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 🧾 Extraction Ubipharm")
        if st.button("➕ Nouvelle base"):
            st.switch_page("pages/ubipharm_page.py")

    with col2:
        st.markdown("### 💰 Extraction Laborex")
        if st.button("➕ Nouveau base"):
            st.switch_page("pages/laborex.py")


    st.markdown("---")
  
elif selected == "📊 Extraction Ubipharm": 
    st.switch_page("pages/ubipharm_page.py")

elif selected == "🧾 Extraction Laborex":
    st.switch_page("pages/laborex.py")





uploaded_file = st.file_uploader("📂 Charger le fichier Excel", type=["xlsx"])

if uploaded_file:
    # 1️⃣ Lecture Excel (suppression des 3 premières lignes)
    df = pd.read_excel(uploaded_file, skiprows=3)

    st.subheader("🔎 Aperçu des données après nettoyage")
    st.dataframe(df.head())

    # 2️⃣ Colonnes
    label_col = df.columns[0]
    vente_cols = df.columns[1::2]  # 1 colonne sur 2 = VENTE

    ventes_df = df[[label_col] + list(vente_cols)]

    # 3️⃣ Exclusion de produits
    produits = ventes_df[label_col].dropna().unique().tolist()

    produits_a_exclure = st.multiselect(
        "🚫 Sélectionner les produits à exclure",
        options=produits
    )

    if produits_a_exclure:
        ventes_df = ventes_df[~ventes_df[label_col].isin(produits_a_exclure)]

    st.subheader("📋 Ventes par zone (format large)")
    st.dataframe(ventes_df)

    # 4️⃣ Format analytique
    ventes_long = ventes_df.melt(
        id_vars=label_col,
        var_name="Zone",
        value_name="Vente"
    )

    # Nettoyage
    ventes_long["Vente"] = pd.to_numeric(ventes_long["Vente"], errors="coerce").fillna(0)

    # 5️⃣ AGRÉGATION PAR ZONE
    ventes_zone = (
        ventes_long
        .groupby("Zone", as_index=False)["Vente"]
        .sum()
        .sort_values("Vente", ascending=False)
    )


    # =====================
    # 📊 GRAPHIQUE BARRES
    # =====================
    st.subheader("📊 Ventes par zone")

    st.bar_chart(
        ventes_zone.set_index("Zone")["Vente"]
    )

    # =====================
    # ⬇️ EXPORT EXCEL
    # =====================
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        ventes_df.to_excel(writer, index=False, sheet_name="Ventes_par_zone")
        ventes_long.to_excel(writer, index=False, sheet_name="Format_analytique")
        ventes_zone.to_excel(writer, index=False, sheet_name="Synthese_par_zone")

    st.download_button(
        "⬇️ Télécharger le fichier Excel",
        data=output.getvalue(),
        file_name="ventes_par_zone.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
