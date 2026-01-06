import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import plotly.express as px
import json
import time
import os

# Configuration de la page
st.set_page_config(
    page_title="CoinAfrique Scraper",
    page_icon="👕",
    layout="wide"
)

# Créer les dossiers nécessaires
os.makedirs("evaluations", exist_ok=True)

# Initialisation session
if 'scraped_data' not in st.session_state:
    st.session_state.scraped_data = None
if 'cleaned_data' not in st.session_state:
    st.session_state.cleaned_data = None

# ============================================
# FONCTIONS DE BASE
# ============================================

def scraping_safe(url, pages=3):
    """Fonction de scraping sécurisée"""
    all_data = []
    
    for page_num in range(1, pages + 1):
        try:
            page_url = f"{url}?page={page_num}" if "?" not in url else f"{url}&page={page_num}"
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(page_url, headers=headers, timeout=30)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                containers = soup.find_all('div', {'class': 'col s6 m4 l3'})
                
                for container in containers:
                    try:
                        title_elem = container.find('p', {'class': 'ad__card-description'})
                        price_elem = container.find('p', {'class': 'ad__card-price'})
                        location_elem = container.find('p', {'class': 'ad__card-location'})
                        img_elem = container.find('img', {'class': 'ad__card-img'})
                        
                        if all([title_elem, price_elem, location_elem, img_elem]):
                            item = {
                                'titre': title_elem.a.text.strip() if title_elem.a else 'Non spécifié',
                                'prix': price_elem.a.text.strip() if price_elem.a else '0 CFA',
                                'localisation': location_elem.span.text.strip() if location_elem.span else 'Non spécifiée',
                                'image': img_elem.get('src', ''),
                                'page': page_num,
                                'date_scraping': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                'url_source': url
                            }
                            all_data.append(item)
                    except:
                        continue
                
                time.sleep(2)  # Respect du serveur
            else:
                st.warning(f"Page {page_num}: Statut {response.status_code}")
                
        except Exception as e:
            st.error(f"Erreur page {page_num}: {str(e)}")
            break
    
    return pd.DataFrame(all_data) if all_data else pd.DataFrame()

# ============================================
# INTERFACE STREAMLIT
# ============================================

def main():
    st.sidebar.title("👕 CoinAfrique Scraper")
    
    menu = st.sidebar.radio(
        "Navigation",
        ["🏠 Accueil", "🔍 Scraper", "📥 Télécharger", "📊 Dashboard", "⭐ Évaluation"]
    )
    
    # Page d'accueil
    if menu == "🏠 Accueil":
        st.title("CoinAfrique Scraper")
        st.markdown("""
        ### Application de scraping et d'analyse de données
        
        **Fonctionnalités :**
        1. 🔍 Scraping multi-pages depuis CoinAfrique
        2. 📥 Export des données en CSV/JSON
        3. 📊 Dashboard interactif
        4. ⭐ Formulaire d'évaluation
        """)
        
        # URLs de test
        st.info("""
        **URLs disponibles :**
        - https://sn.coinafrique.com/categorie/vetements-homme/
        - https://sn.coinafrique.com/categorie/telephones
        - https://sn.coinafrique.com/categorie/ordinateurs
        """)
    
    # Page de scraping
    elif menu == "🔍 Scraper":
        st.title("🔍 Scraper des Données")
        
        col1, col2 = st.columns(2)
        
        with col1:
            url = st.text_input(
                "URL à scraper",
                value="https://sn.coinafrique.com/categorie/telephones"
            )
        
        with col2:
            pages = st.slider("Nombre de pages", 1, 5, 2)
        
        if st.button("🚀 Lancer le scraping", type="primary"):
            with st.spinner("Scraping en cours..."):
                df = scraping_safe(url, pages)
                
                if not df.empty:
                    st.session_state.scraped_data = df
                    st.success(f"✅ {len(df)} annonces trouvées !")
                    
                    # Aperçu
                    st.dataframe(df, use_container_width=True)
                else:
                    st.warning("Aucune donnée trouvée. Essayez une autre URL.")
    
    # Page de téléchargement
    elif menu == "📥 Télécharger":
        st.title("📥 Télécharger les Données")
        
        if st.session_state.scraped_data is not None:
            df = st.session_state.scraped_data
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric("Annonces", len(df))
            
            with col2:
                st.metric("Colonnes", len(df.columns))
            
            # Format CSV
            csv = df.to_csv(index=False)
            st.download_button(
                label="📥 Télécharger CSV",
                data=csv,
                file_name=f"scraping_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
            
            # Format JSON
            json_str = df.to_json(orient='records', indent=2)
            st.download_button(
                label="📥 Télécharger JSON",
                data=json_str,
                file_name=f"scraping_{datetime.now().strftime('%Y%m%d')}.json",
                mime="application/json"
            )
            
            st.dataframe(df, use_container_width=True)
        else:
            st.warning("Aucune donnée disponible. Scrapez d'abord des données.")
    
    # Page Dashboard
    elif menu == "📊 Dashboard":
        st.title("📊 Dashboard")
        
        if st.session_state.scraped_data is not None:
            df = st.session_state.scraped_data
            
            # Nettoyage simple
            if 'prix' in df.columns:
                # Extraire les valeurs numériques des prix
                df['prix_numerique'] = df['prix'].str.extract(r'(\d+)').astype(float)
            
            # Métriques
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Total annonces", len(df))
            
            with col2:
                if 'prix_numerique' in df.columns:

                    avg
