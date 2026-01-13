import streamlit as st

st.set_page_config(page_title="BI Pharma Mali", page_icon="💊", layout="wide")

st.title("MABOU BI Pharma Mali")
st.write("Bienvenue dans votre application multi-grossistes.")

# Ensemble de boutons pour choisir le grossiste
grossiste = st.radio(
    "Choisissez un grossiste",
    ["Ubipharm", "Copharma", "Sodipharm"],
    horizontal=True
)

if grossiste == "Ubipharm":
    st.page_link("pages/ubipharm_page.py", label="➡️ Aller à la page Ubipharm")
elif grossiste == "Copharma":
    st.page_link("pages/copharma_page.py", label="➡️ Aller à la page Copharma")
elif grossiste == "Sodipharm":
    st.page_link("pages/sodipharm_page.py", label="➡️ Aller à la page Sodipharm")
