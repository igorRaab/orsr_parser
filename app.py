import streamlit as st
import requests
import json
import pandas as pd
import plotly.graph_objects as go

# --- KONFIGURÁCIA A ŠTÝLOVANIE ---
st.set_page_config(
    page_title="AI Risk Oracle 2026", 
    page_icon="⚡", 
    layout="wide", 
    initial_sidebar_state="expanded"
)

# Vlastné moderné CSS pre Streamlit
st.markdown("""
    <style>
    /* Gradient pre celú stránku */
    .stApp {
        background: linear-gradient(135deg, #e0f2f7 0%, #c1d9e6 100%);
    }

    /* Gradient a tieň pre header */
    .st-emotion-cache-18ni7ap { /* Cieľ pre hlavný header */
        background: linear-gradient(45deg, #004e92 0%, #000428 100%);
        color: white;
        padding: 20px 0;
        border-radius: 15px;
        box-shadow: 0 8px 16px rgba(0, 0, 0, 0.2);
        margin-bottom: 30px;
    }

    /* Tlačidlá */
    .stButton>button {
        background-color: #004e92;
        color: white;
        border: none;
        padding: 10px 20px;
        border-radius: 8px;
        font-weight: bold;
        transition: all 0.2s ease-in-out;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
    }
    .stButton>button:hover {
        background-color: #007bff;
        box-shadow: 0 6px 12px rgba(0, 0, 0, 0.15);
        transform: translateY(-2px);
    }

    /* Input polia */
    .stTextInput>div>div>input, .stTextArea>div>div>textarea {
        border-radius: 8px;
        border: 1px solid #a7b9c9;
        box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.06);
    }

    /* Zvýraznenie Rizika v tabuľke (cez HTML) */
    .risk-score-low { background-color: #e6ffe6; color: #1a73e8; font-weight: bold; border-radius: 4px; padding: 2px 5px; }
    .risk-score-medium { background-color: #fff9e6; color: #e8991a; font-weight: bold; border-radius: 4px; padding: 2px 5px; }
    .risk-score-high { background-color: #ffe6e6; color: #d32f2f; font-weight: bold; border-radius: 4px; padding: 2px 5px; }
    .risk-score-critical { background-color: #ffcccc; color: #8a0a0a; font-weight: bold; border-radius: 4px; padding: 2px 5px; animation: pulse 1.5s infinite; }

    @keyframes pulse {
        0% { box-shadow: 0 0 0 0 rgba(255,0,0, 0.4); }
        70% { box-shadow: 0 0 0 10px rgba(255,0,0, 0); }
        100% { box-shadow: 0 0 0 0 rgba(255,0,0, 0); }
    }

    /* Kontajnery pre výsledky */
    .st-emotion-cache-czk5ad { /* Cieľ pre st.container */
        background-color: #ffffff;
        padding: 25px;
        border-radius: 12px;
        box-shadow: 0 6px 12px rgba(0,0,0,0.1);
        margin-top: 20px;
    }
    
    .stAlert {
        border-radius: 8px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- GROQ API KLIENT ---
# Načíta kľúč z "trezoru" Streamlitu (ak tam nie je, vráti prázdny reťazec)
GROQ_API_KEY = st.secrets.get("GROQ_API_KEY", "")

def analyze_with_groq(text_data, company_ico=None):
    url = "https://api.groq.com/openai/v1/chat/completions"
    
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    
    # Sofistikovaný prompt pre Llama 3 (zdôrazňuje slovenskú terminológiu)
    prompt_template = f"""
    Si elitný senior underwriter špecializovaný na poistenie všeobecnej zodpovednosti podnikateľov v slovenskom právnom prostredí.
    Tvojou úlohou je vykonať hĺbkovú analýzu predmetov činnosti firmy z Obchodného registra SR.

    Ak je k dispozícii IČO: {company_ico if company_ico else 'N/A'}, použij svoju internú databázu znalostí na kontextualizáciu firmy (vek, odvetvie, reputácia, ak je známa).
    
    Pre KAŽDÝ predmet činnosti:
    1.  **Činnosť:** Pôvodný text.
    2.  **Odhadovaný NACE kód:** 4-miestny štatistický kód (napr. 43.12 - Prípravné práce pre stavby).
    3.  **Rizikový Rating (0-100):** Číselná hodnota, kde 0 je minimálne riziko a 100 je extrémne kritické.
        * 0-25: Nízke
        * 26-50: Stredné
        * 51-75: Vysoké
        * 76-100: Kritické
    4.  **Kľúčové poistné nebezpečenstvo:** Stručný popis hlavného rizika pre poisťovňu (napr. regresné nároky, škody na zdraví tretích osôb, finančná strata).
    5.  **Red Flag:** Áno/Nie (ak činnosť vyžaduje špeciálny dotazník, je zvyčajne vylúčená alebo vyžaduje extrémne vysoký limit).

    Následne pod tabuľku pridaj sekciu **'Underwritingové Odporúčania & Tipy pre Makléra'**, ktorá bude obsahovať:
    * **Celkové Skóre Rizika Firmy:** Priemer rizikových ratingov všetkých činností (0-100).
    * **Odporúčané Limity Plnenia:** Návrh minimálnych a optimálnych limitov pre poistenie zodpovednosti.
    * **Kritické Doložky a Výluky:** Zoznam doložiek (napr. doložka o subdodávateľoch, doložka o prácach vo výškach) a výluk, ktoré sú pre tento profil kľúčové v slovenskej praxi.
    * **Cross-Sell Tipy:** Návrhy na dodatočné poistenia (napr. poistenie kybernetických rizík, poistenie majetku, D&O).
    * **Doplňujúce Otázky pre Klienta:** Konkrétne otázky, ktoré by mal maklér položiť klientovi.

    ODPOVEĎ VRÁŤ VŽDY A VÝHRADNE AKO ČISTÝ HTML KÓD.
    Pre rizikové skóre použi HTML classy: risk-score-low, risk-score-medium, risk-score-high, risk-score-critical
    
    Analýza predmetov činnosti (prepis z ORSR):
    {text_data}
    """
    
    payload = {
        "model": MODEL_NAME,
        "messages": [
            {"role": "system", "content": "Si špičkový underwriter, odpovedáš iba HTML."},
            {"role": "user", "content": prompt_template}
        ],
        "temperature": 0.1, # Nízka teplota pre faktickú presnosť
        "max_tokens": 4096 # Zvýšené pre detailné reporty
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status() # Vyhodí chybu pre HTTP 4xx/5xx
        result = response.json()['choices'][0]['message']['content']
        return result
    except requests.exceptions.HTTPError as http_err:
        error_detail = response.json() if response.text else "N/A"
        return f"<div style='color:red;'>API chyba ({response.status_code}): {http_err} <br>Detail: {json.dumps(error_detail)}</div>"
    except Exception as e:
        return f"<div style='color:red;'>Neočakávaná chyba: {str(e)}</div>"

# --- HLAVNÁ APLIKÁCIA STREAMLIT ---
st.markdown("""
    <h1 style="text-align: center; color: white;">
        <span style="font-size: 1.2em;">⚡</span> AI Risk Oracle 2026
    </h1>
    <p style="text-align: center; color: white; font-size: 1.1em; opacity: 0.9;">
        Automatizovaná expertná analýza rizík podnikov pre poistencov
    </p>
""", unsafe_allow_html=True)

# Bočný panel pre API kľúč a info
with st.sidebar:
    st.title("🛡️ Risk Oracle")
    st.info("Systém je pripravený na analýzu. API kľúč je bezpečne spravovaný administrátorom.")

    st.markdown("---")
    st.info("""
        **O tomto nástroji:**
        Tento nástroj využíva pokročilú AI (Llama 3 bežiacu na Groq infraštruktúre) 
        na hĺbkovú analýzu predmetov činnosti firmy z Obchodného registra SR.
        Výsledkom je detailný rizikový profil a konkrétne odporúčania pre underwritera.
        
        **Prečo Groq?** Poskytuje extrémne rýchle a štedré bezplatné API pre Llama 3 modely.
        Váš kľúč získate na [console.groq.com](https://console.groq.com/).
    """)

# Vstup pre IČO alebo manuálny text
st.markdown("### Vstup pre analýzu")
col1, col2 = st.columns(2)

with col1:
    ico_input = st.text_input("Zadajte IČO spoločnosti (pre automatické vyhľadanie):", placeholder="Napr. 35763469")

with col2:
    manual_text_area = st.text_area("Alebo prilepte text predmetov činnosti manuálne:", height=150)

# Tlačidlo pre analýzu
if st.button("🚀 Spustiť Hĺbkovú Analýzu Rizík", use_container_width=True):
    if not GROQ_API_KEY or GROQ_API_KEY == "TU_VLOZTE_VAS_GROQ_KEY":
        st.error("❗ Prosím, vložte Váš Groq API kľúč v ľavom bočnom paneli.")
    elif ico_input:
        # Tu by sme v ideálnom prípade volali API na stiahnutie dát podľa IČO
        # Pre demo, pošleme IČO AI, nech si to sama vyhľadá (Groq to často zvládne)
        st.info(f"AI bude vyhľadávať dáta pre IČO: **{ico_input}** a analyzovať...")
        with st.spinner("🧠 AI spracováva dáta a generuje expertný report..."):
            report_html = analyze_with_groq(f"Vyhľadaj a analyzuj predmety činnosti pre IČO {ico_input} zo slovenských registrov.", company_ico=ico_input)
            st.markdown("---")
            st.subheader("✅ Analýza Dokončená")
            st.html(report_html)
            # stiahnutie reportu (pre HTML - PDF vyžaduje viac kódu)
            st.download_button(
                label="⬇️ Stiahnuť HTML Report",
                data=report_html,
                file_name=f"Risk_Report_{ico_input if ico_input else 'manual'}.html",
                mime="text/html",
                use_container_width=True
            )

    elif manual_text_area:
        st.info("AI bude analyzovať manuálne vložené dáta.")
        with st.spinner("🧠 AI spracováva dáta a generuje expertný report..."):
            report_html = analyze_with_groq(manual_text_area)
            st.markdown("---")
            st.subheader("✅ Analýza Dokončená")
            st.html(report_html)
            st.download_button(
                label="⬇️ Stiahnuť HTML Report",
                data=report_html,
                file_name="Risk_Report_manual.html",
                mime="text/html",
                use_container_width=True
            )
    else:
        st.warning("Zadajte IČO alebo prilepte text predmetov činnosti pre spustenie analýzy.")

st.markdown("---")
st.caption("© 2026 AI Risk Solutions | Využíva **Llama 3** na platforme **Groq**")
