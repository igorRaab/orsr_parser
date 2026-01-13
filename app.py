import streamlit as st
import requests
import json
import pandas as pd

# --- 1. KONFIGURÁCIA STRÁNKY ---
st.set_page_config(
    page_title="AI Risk Oracle 2026", 
    page_icon="🛡️", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Načítanie kľúča zo Secrets (Nastavuje sa v Streamlit Cloud Dashboarde)
GROQ_API_KEY = st.secrets.get("GROQ_API_KEY", "")
MODEL_TO_USE = "llama-3.3-70b-versatile" 

# --- 2. MODERNÝ FINANČNÝ DESIGN (CSS) ---
st.markdown("""
    <style>
    .stApp { background-color: #f4f7f9; }
    
    /* Header s hĺbkou */
    .main-header { 
        background: linear-gradient(135deg, #002f5d 0%, #000428 100%);
        color: white; padding: 3rem; border-radius: 25px; text-align: center;
        box-shadow: 0 15px 35px rgba(0,0,0,0.2); margin-bottom: 3rem;
        border-bottom: 5px solid #0072ff;
    }
    
    /* Styling tabuliek, ktoré vygeneruje AI */
    .risk-table { width: 100%; border-collapse: collapse; margin: 20px 0; font-size: 0.9em; border-radius: 10px; overflow: hidden; }
    .risk-table thead tr { background-color: #004e92; color: #ffffff; text-align: left; }
    .risk-table th, .risk-table td { padding: 12px 15px; border-bottom: 1px solid #dddddd; }
    
    /* Farebné triedy pre rizikové skóre */
    .risk-score-low { color: #2ecc71; font-weight: bold; background: #eafaf1; padding: 4px 8px; border-radius: 5px; }
    .risk-score-medium { color: #f39c12; font-weight: bold; background: #fef5e7; padding: 4px 8px; border-radius: 5px; }
    .risk-score-high { color: #e67e22; font-weight: bold; background: #fdf2e9; padding: 4px 8px; border-radius: 5px; }
    .risk-score-critical { color: #c0392b; font-weight: bold; background: #f9ebea; padding: 4px 8px; border-radius: 5px; border: 1px solid #c0392b; }

    /* Sekcia odporúčaní */
    .analysis-summary { background: white; padding: 2rem; border-radius: 15px; box-shadow: 0 4px 12px rgba(0,0,0,0.05); margin-top: 2rem; border-left: 8px solid #004e92; }
    
    .stButton>button {
        background: linear-gradient(90deg, #004e92 0%, #0072ff 100%);
        color: white; border: none; font-weight: bold; padding: 1rem;
        border-radius: 12px; transition: 0.4s; font-size: 1.1rem;
    }
    .stButton>button:hover { transform: translateY(-3px); box-shadow: 0 10px 20px rgba(0,114,255,0.3); }
    </style>
    
    <div class="main-header">
        <h1>🛡️ AI Underwriting Oracle v.2026</h1>
        <p>Chief Underwriting Officer Level Analysis | Slovak Market Specialization</p>
    </div>
    """, unsafe_allow_html=True)

# --- 3. BOČNÝ PANEL (SIDEBAR) ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/950/950008.png", width=100)
    st.title("Systémový Status")
    st.success("📡 Prepojenie na registre: OK")
    st.info(f"🧠 Engine: {MODEL_TO_USE}")
    
    st.markdown("---")
    st.markdown("### 🔍 Metodika analýzy")
    st.write("""
    - **NACE Rev. 2** klasifikácia.
    - **Exposure Weighting** (váženie rizika).
    - **Regresná analýza** (Soc. poisťovňa).
    - **CSL** (Combined Single Limit) návrhy.
    """)
    
    st.markdown("---")
    st.caption("Určené výhradne pre interné potreby poisťovacích profesionálov.")

# --- 4. MASTER PROMPT LOGIKA ---
def run_master_analysis(text_data, ico=None):
    if not GROQ_API_KEY:
        st.error("Chýba API kľúč! Zadajte ho do Secrets v Streamlit Dashboarde.")
        return None

    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
    
    # Implementácia "Najlepšieho promptu na svete"
    master_prompt = f""
    Si elitný Chief Underwriting Officer (CUO) s 20-ročnou
