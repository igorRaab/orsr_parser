import streamlit as st
import requests
import json
import pandas as pd
import plotly.graph_objects as go

# --- 1. ZÁKLADNÁ KONFIGURÁCIA ---
st.set_page_config(page_title="Risk Oracle 2026", page_icon="🛡️", layout="wide")

# Načítanie kľúča zo Secrets (Nastavíte v Streamlit Cloud Dashboarde)
GROQ_API_KEY = st.secrets.get("GROQ_API_KEY", "")
MODEL_NAME = "llama3-70b-8192" # Definícia, ktorá chýbala

# --- 2. ŠTÝLOVANIE ---
st.markdown("""
    <style>
    .stApp { background: linear-gradient(135deg, #f0f4f8 0%, #d7e2eb 100%); }
    .main-header { 
        background: linear-gradient(90deg, #004e92 0%, #000428 100%);
        color: white; padding: 2rem; border-radius: 15px; text-align: center;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1); margin-bottom: 2rem;
    }
    .risk-score-low { color: #28a745; font-weight: bold; }
    .risk-score-medium { color: #fd7e14; font-weight: bold; }
    .risk-score-high { color: #dc3545; font-weight: bold; }
    </style>
    <div class="main-header">
        <h1>🛡️ AI Underwriting Oracle</h1>
        <p>Expertná analýza rizík firiem v reálnom čase</p>
    </div>
    """, unsafe_allow_html=True)

# --- 3. LOGIKA ANALÝZY ---
def analyze_with_groq(text_data, company_ico=None):
    if not GROQ_API_KEY:
        return "<p style='color:red;'>Chyba: API kľúč nie je nastavený v Secrets!</p>"
    
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    
    # Použijeme najnovší model 2026, ktorý je teraz v Groq zadarmo a stabilný
    MODEL_TO_USE = "llama-3.3-70b-versatile" 
    
    prompt = f"""
    Si senior underwriter. Analyzuj predmety činnosti firmy (IČO: {company_ico if company_ico else 'manuálny vstup'}).
    Vráť HTML TABUĽKU (Činnosť, NACE, Riziko 1-100, Red Flag) a pod to ODBORNÉ ODPORÚČANIA.
    Dáta: {text_data}
    """
    
    # Payload musí byť presne podľa OpenAI štandardu
    payload = {
        "model": MODEL_TO_USE,
        "messages": [
            {"role": "system", "content": "Odpovedaj výhradne v HTML kóde bez markdown značiek."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.1  # Zníženie na 0.1 pre maximálnu stabilitu
    }
    
    try:
        r = requests.post(url, headers=headers, json=payload)
        
        # Ak nastane chyba 400, vypíšeme presný dôvod od Groq
        if r.status_code != 200:
            return f"<p style='color:red;'>API Error {r.status_code}: {r.json().get('error', {}).get('message', 'Neznáma chyba')}</p>"
            
        return r.json()['choices'][0]['message']['content'].replace("```html", "").replace("```", "")
    except Exception as e:
        return f"<p style='color:red;'>Chyba spojenia: {str(e)}</p>"

# --- 4. UI ROZHRANIE ---
col1, col2 = st.columns(2)
with col1:
    ico_input = st.text_input("Zadajte IČO (AI vyhľadá firmu):", placeholder="Napr. 35763469")
with col2:
    manual_text = st.text_area("Alebo vložte text manuálne:", height=68)

if st.button("🚀 Spustiť analýzu", use_container_width=True):
    if ico_input or manual_text:
        with st.spinner("🧠 AI analyzuje rizikový profil..."):
            input_data = f"Vyhľadaj a analyzuj predmety činnosti pre IČO {ico_input}" if ico_input else manual_text
            report = analyze_with_groq(input_data, ico_input)
            st.markdown("---")
            st.html(report)
    else:
        st.warning("Prosím zadajte IČO alebo text.")

st.caption("© 2026 Underwriting Showcase | Powered by Groq & Llama 3")
