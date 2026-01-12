import streamlit as st
import pandas as pd

def run():
    st.header("📦 Gestion des stocks")
    # Exemple fictif
    data = {
        "Produit": ["ALCOF-C", "FEVERLET", "SOLFER"],
        "Stock": [200, 150, 80]
    }
    df = pd.DataFrame(data)
    st.dataframe(df)
    