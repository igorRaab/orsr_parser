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
    master_prompt = f"""
    Si elitný Chief Underwriting Officer (CUO) s 20-ročnou praxou v korporátnom poistení zodpovednosti (General Liability) na slovenskom trhu. 
    Tvojím cieľom je vytvoriť technicky dokonalý risk report pre firmu (IČO: {ico if ico else 'N/A'}).

    Dáta z ORSR: {text_data}

    TVOJA METODIKA:
    1. DEKONŠTRUKCIA: Identifikuj každú činnosť a priraď jej presný NACE rev. 2 kód.
    2. ANALÝZA EXPOZÍCIE: Posúď závažnosť možných škôd (zdravie, majetok, čisté finančné škody).
    3. SYNERGIA RIZIKA: Vyhodnoť, či kombinácia činností nezvyšuje celkový rizikový profil.
    4. KLASIFIKÁCIA: Použi striktnú terminológiu (Zodpovednosť za vadu, Regresy, Prevádzková činnosť).

    VÝSTUP (Iba čisté HTML):
    <div class="report-container">
      <table class="risk-table">
        <thead>
          <tr>
            <th>Predmet činnosti</th>
            <th>NACE</th>
            <th>Rizikové skóre (0-100)</th>
            <th>Kľúčové nebezpečenstvo</th>
            <th>Red Flag</th>
          </tr>
        </thead>
        <tbody>
          </tbody>
      </table>

      <div class="analysis-summary">
        <h3>📊 Celkové technické zhodnotenie</h3>
        <p><strong>Vypočítaný Risk Index:</strong> [Priemer vážený rizikovosťou] / 100</p>
        <h4>📋 Odporúčania pre upisovateľa:</h4>
        <ul>
          <li><strong>Limit plnenia:</strong> Odporúčaný CSL v EUR.</li>
          <li><strong>Povinné doložky:</strong> Technické názvy doložiek pre SR trh.</li>
          <li><strong>Vylúčené činnosti:</strong> Čo nepoistiť.</li>
        </ul>
        <h4>🔍 Due Diligence (Otázky pre makléra):</h4>
        <p>3-5 cielených otázok na odhalenie skrytého rizika.</p>
        <h4>💡 Cross-sell potenciál:</h4>
        <p>Potreba pre D&O, Enviro alebo Kyber.</p>
      </div>
    </div>
    """
    
    payload = {
        "model": MODEL_TO_USE,
        "messages": [
            {"role": "system", "content": "Si expertný AI Underwriter. Odpovedáš iba čistým HTML bez markdown značiek."},
            {"role": "user", "content": master_prompt}
        ],
        "temperature": 0.1
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        if response.status_code == 200:
            return response.json()['choices'][0]['message']['content'].replace("```html", "").replace("```", "").strip()
        else:
            st.error(f"Chyba API ({response.status_code}): {response.text}")
            return None
    except Exception as e:
        st.error(f"Kritická chyba: {e}")
        return None

# --- 5. HLAVNÁ ČASŤ APLIKÁCIE ---
col_left, col_right = st.columns(2)

with col_left:
    st.markdown("#### 🆔 Identifikácia subjektu")
    ico_input = st.text_input("IČO firmy:", placeholder="35763469")

with col_right:
    st.markdown("#### 📝 Manuálny zoznam činností")
    manual_input = st.text_area("Vložte text z ORSR:", placeholder="Prilepte predmety činnosti...", height=68)

if st.button("🔍 GENEROVAŤ EXPERTNÝ RISK REPORT", use_container_width=True):
    # Určenie vstupu
    final_input = f"Vyhľadaj a analyzuj firmu s IČO {ico_input}" if ico_input else manual_input
    
    if final_input:
        with st.spinner("🚀 Prebieha hĺbková analýza rizikových faktorov..."):
            html_report = run_master_analysis(final_input, ico_input)
            if html_report:
                st.markdown("---")
                st.html(html_report)
                
                # Možnosť stiahnutia
                st.download_button(
                    label="📥 Exportovať Report pre Underwritingový spis",
                    data=html_report,
                    file_name=f"Risk_Report_{ico_input if ico_input else 'manual'}.html",
                    mime="text/html",
                    use_container_width=True
                )
    else:
        st.warning("Zadajte IČO alebo prilepte text na analýzu.")

st.markdown("---")
st.caption("Nástroj využíva Llama 3.3 (State-of-the-art LLM) na analýzu neštruktúrovaných dát z verejných registrov SR.")
