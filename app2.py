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
   Si elitný Chief Underwriting Officer (CUO) s 20-ročnou praxou v korporátnom poistení zodpovednosti (General Liability) na slovenskom trhu. Tvojím cieľom je vytvoriť technicky dokonalý risk report, ktorý slúži ako podklad pre upísanie rizika.

KONTEXT: 
Analyzuješ firmu s IČO: {ico if ico else 'N/A'}. 
Dáta z ORSR: {text_data}

TVOJA METODIKA (Postupuj podľa týchto krokov):
1. DEKONŠTRUKCIA: Identifikuj každú činnosť a priraď jej presný NACE rev. 2 kód podľa štatistickej klasifikácie SR.
2. ANALÝZA EXPOZÍCIE: Posúď frekvenciu a závažnosť možných škôd (zdravie, majetok, čisté finančné škody).
3. SYNERGIA RIZIKA: Ak má firma v ORSR protichodné činnosti (napr. administratíva vs. vŕtanie studní), celkové riziko sa nezemeruje, ale stúpa kvôli nejasnému zameraniu.
4. KLASIFIKÁCIA: Použi striktnú terminológiu slovenského poistného trhu (Zodpovednosť za vadu výrobku, Zodpovednosť za škodu z prevádzkovej činnosti, Regresy Sociálnej poisťovne).

VÝSTUPNÝ FORMÁT (Iba čisté HTML bez úvodných rečí):

<div class="report-container">
  <h2>🛡️ Underwriting Risk Report: {ico if ico else 'Manuálna analýza'}</h2>
  
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
      <tr>
        <td>[Pôvodný text]</td>
        <td>[Kód - Názov]</td>
        <td class="[class]"> [Body] </td>
        <td>[Technický popis expozície]</td>
        <td>[⚠️ ÁNO / NIE]</td>
      </tr>
    </tbody>
  </table>

  <div class="analysis-summary">
    <h3>📊 Celkové technické zhodnotenie</h3>
    <p><strong>Vypočítaný Risk Index:</strong> [Priemer vážený rizikovosťou] / 100</p>
    
    <h4>📋 Odporúčania pre upisovateľa:</h4>
    <ul>
      <li><strong>Limit plnenia:</strong> Odporúčaný Combined Single Limit (CSL) v EUR vzhľadom na charakter činnosti.</li>
      <li><strong>Povinné doložky:</strong> (napr. Doložka o prácach na cudzích veciach, Čisté finančné škody, Nároky z titulu porušenia práv duševného vlastníctva).</li>
      <li><strong>Vylúčené činnosti:</strong> Ktoré činnosti z ORSR sa nesmú poistiť v štandardnom krytí.</li>
    </ul>

    <h4>🔍 Due Diligence (Otázky pre makléra):</h4>
    <p>Polož 3-5 cielených otázok, ktoré odhalia skutočný rozsah rizika (napr. subdodávatelia v %, práce v zahraničí, obrat v USA/Kanade).</p>
    
    <h4>💡 Cross-sell potenciál:</h4>
    <p>Identifikuj potrebu pre D&O, Enviro-zodpovednosť alebo Professional Indemnity na základe zapísaných činností.</p>
  </div>
</div>

STRIKTNÉ PRAVIDLÁ PRE HTML:
- Pre rizikové skóre použi CLASSY: risk-score-low (0-25), risk-score-medium (26-50), risk-score-high (51-75), risk-score-critical (76-100).
- Nepoužívaj ```html značky, vráť len kód.
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
# --- PÄTIČKA ---
st.markdown("---")
st.markdown("<p style='text-align: center; opacity: 0.6;'>Nástroj slúži na podporu rozhodovania. Finálny verdikt patrí pod kompetenciu upisovateľa.</p>", unsafe_allow_html=True)
