import streamlit as st
import requests
import json

# --- KONFIGURÁCIA STRÁNKY ---
st.set_page_config(page_title="ORSR Risk AI Parser", page_icon="🛡️", layout="wide")

# --- ŠTÝLOVANIE ---
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stButton>button { width: 100%; border-radius: 5px; height: 3em; background-color: #004e92; color: white; }
    .risk-low { color: green; font-weight: bold; }
    .risk-med { color: orange; font-weight: bold; }
    .risk-high { color: red; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- BOČNÝ PANEL (Konfigurácia) ---
with st.sidebar:
    st.title("⚙️ Nastavenia")
    api_key = st.text_input("Vložte Gemini API Kľúč", type="password", value="")
    model_choice = st.selectbox("Model", ["gemini-3-flash-preview", "gemini-2.0-flash"])
    st.info("Tento nástroj analyzuje predmety činnosti z ORSR pomocou AI a priraďuje im rizikový profil.")

# --- HLAVNÁ ČASŤ ---
st.title("🛡️ Underwriting AI Oracle")
st.subheader("Analýza predmetov činnosti a NACE kódov")

input_text = st.text_area("Prilepte predmety činnosti z ORSR:", height=200, placeholder="Napr.: Výroba kovových konštrukcií, Nákladná cestná doprava...")

if st.button("Spustiť hĺbkovú analýzu"):
    if not input_text:
        st.warning("Prosím, vložte text na analýzu.")
    else:
        with st.spinner("🚀 Gemini 3 analyzuje riziká..."):
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_choice}:generateContent?key={api_key}"
            
            prompt = f"""
            Si senior underwriter. Analyzuj tieto činnosti z ORSR.
            VRÁŤ IBA ČISTÉ HTML (bez markdown značiek).
            HTML musí obsahovať:
            1. Štýlovanú tabuľku (Class 'risk-table') so stĺpcami: Činnosť, NACE, Riziko, Red Flag.
            2. Sekciu 'Odporúčania' s bodmi pre doložky a limity.
            
            Text: {input_text}
            """
            
            payload = {"contents": [{"parts": [{"text": prompt}]}]}
            
            try:
                response = requests.post(url, json=payload)
                response.raise_for_status()
                result = response.json()['candidates'][0]['content']['parts'][0]['text']
                
                # Vyčistenie a zobrazenie
                clean_html = result.replace("```html", "").replace("```", "").strip()
                
                # Vizualizácia výsledku v kontajneri
                st.markdown("---")
                st.write("### 📊 Výsledok Underwritingového Posúdenia")
                st.html(clean_html)
                
                # Možnosť stiahnutia (jednoduchá verzia)
                st.download_button("Stiahnuť report (HTML)", clean_html, file_name="risk_report.html", mime="text/html")
                
            except Exception as e:
                st.error(f"Chyba: {e}")

# --- PÄTIČKA ---
st.markdown("---")
st.caption("© 2026 Micro-SaaS Underwriting Tool | Powered by Gemini 3.0")
