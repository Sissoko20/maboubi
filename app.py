import streamlit as st
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
    st.caption("© 2026 MABOU-INSTRUMED - Système de gestion de données pharmaceutiques.")

elif selected == "📊 Extraction Ubipharm": 
    st.switch_page("pages/ubipharm_page.py")

elif selected == "🧾 Extraction Laborex":
    st.switch_page("pages/laborex.py")






