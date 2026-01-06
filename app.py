import streamlit as st
import pandas as pd

# Configuration MINIMALE - PAS de layout="wide"
st.set_page_config(page_title="CoinAfrique Scraper", page_icon="👕")

st.title("👕 CoinAfrique Scraper")
st.write("Application en cours de configuration...")

# Navigation simple
option = st.selectbox("Choisissez une action:", ["Accueil", "Scraper", "Dashboard"])

if option == "Accueil":
    st.write("""
    ### Bienvenue sur CoinAfrique Scraper
    
    Fonctions disponibles:
    1. 🔍 Scraping de données
    2. 📥 Téléchargement CSV/JSON
    3. 📊 Dashboard interactif
    """)
    
elif option == "Scraper":
    st.write("Fonction de scraping à venir...")
    if st.button("Test"):
        df = pd.DataFrame({"Test": [1, 2, 3], "Data": ["A", "B", "C"]})
        st.dataframe(df)
        
elif option == "Dashboard":
    st.write("Dashboard à venir...")

