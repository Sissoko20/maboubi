import streamlit as st
import pandas as pd
import plotly.express as px

def run():
    st.header("📊 Analyse des ventes")
    # Exemple de DataFrame fictif
    data = {
        "Région": ["Bamako", "Kayes", "Sikasso"],
        "Ventes": [1200, 800, 950]
    }
    df = pd.DataFrame(data)

    st.dataframe(df)

    fig = px.bar(df, x="Région", y="Ventes", title="Ventes par région")
    st.plotly_chart(fig, use_container_width=True)
