import streamlit as st
import requests
from fpdf import FPDF
import base64

# --- 1. KONFIGURÁCIA ---
st.set_page_config(page_title="Risk Oracle PDF", page_icon="🛡️", layout="wide")

GROQ_API_KEY = st.secrets.get("GROQ_API_KEY", "")
MODEL_TO_USE = "llama-3.3-70b-versatile"

# Inicializácia pamäte (Session State)
if 'analysis_result' not in st.session_state:
    st.session_state.analysis_result = None
if 'user_input' not in st.session_state:
    st.session_state.user_input = ""

# --- 2. FUNKCIA PRE PDF ---
class PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 15)
        self.cell(0, 10, 'Underwriting Risk Report 2026', 0, 1, 'C')
        self.ln(10)

def create_pdf(text_content):
    pdf = PDF()
    pdf.add_page()
    pdf.set_font("Arial", size=11)
    # Odstránenie HTML značiek pre čisté PDF (jednoduchá verzia)
    clean_text = text_content.replace('<li>', '- ').replace('</li>', '\n').replace('<br>', '\n')
    import re
    clean_text = re.sub('<[^<]+?>', '', clean_text)
    
    pdf.multi_cell(0, 10, txt=clean_text.encode('latin-1', 'replace').decode('latin-1'))
    return pdf.output(dest='S').encode('latin-1')

# --- 3. DIZAJN ---
st.markdown("""
    <style>
    .stApp { background-color: #f4f7f9; }
    .main-header { 
        background: #002f5d; color: white; padding: 2rem; 
        border-radius: 15px; text-align: center; margin-bottom: 2rem;
    }
    </style>
    <div class="main-header">
        <h1>🛡️ AI Underwriting Oracle</h1>
        <p>Profesionálna analýza predmetov činnosti z ORSR</p>
    </div>
    """, unsafe_allow_html=True)

# --- 4. LOGIKA ---
def analyze_data(text):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
    
    prompt = f"""
    Si elitný senior underwriter špecializovaný na poistenie všeobecnej zodpovednosti podnikateľov v slovenskom právnom prostredí.
    Tvojou úlohou je vykonať hĺbkovú analýzu predmetov činnosti firmy z Obchodného registra SR.  
    
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
    {user_input}
    """
    
    payload = {
        "model": MODEL_TO_USE,
        "messages": [{"role": "system", "content": "Si expert na poistenie. Odpovedaj v HTML."},
                     {"role": "user", "content": prompt}],
        "temperature": 0.1
    }
    
    try:
        r = requests.post(url, headers=headers, json=payload)
        return r.json()['choices'][0]['message']['content'].replace("```html", "").replace("```", "")
    except:
        return "Chyba pri generovaní analýzy."

# --- 5. UI ---
# Používame session_state pre input
st.session_state.user_input = st.text_area("Vložte predmety činnosti z ORSR:", 
                                         value=st.session_state.user_input, 
                                         height=200)

col1, col2 = st.columns([1, 4])

if col1.button("🔍 Analyzovať"):
    if st.session_state.user_input:
        with st.spinner("Generujem expertný report..."):
            st.session_state.analysis_result = analyze_data(st.session_state.user_input)
    else:
        st.warning("Vložte text.")

if st.session_state.analysis_result:
    st.markdown("---")
    st.html(st.session_state.analysis_result)
    
    # Generovanie PDF
    pdf_bytes = create_pdf(st.session_state.analysis_result)
    
    st.download_button(
        label="📄 Stiahnuť report v PDF",
        data=pdf_bytes,
        file_name="UW_Risk_Report.pdf",
        mime="application/pdf",
        use_container_width=True
    )

st.sidebar.title("Info")
st.sidebar.info("Tento nástroj spracováva manuálne vložené dáta pre maximálnu presnosť.")
