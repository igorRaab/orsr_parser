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
    Pôsob ako elitný senior underwriter špecializovaný na poistenie všeobecnej zodpovednosti podnikateľov v slovenskom poistnom, právnom a trhovom prostredí s viac ako 20 rokmi praxe. Máš hlboké znalosti slovenských poistných podmienok, výluk, štandardov likvidácie škôd, špecifík maklérskej praxe a komerčných prevádzkových rizík. Tvojou úlohou je: 1) vykonať hĺbkovú underwriting analýzu spoločnosti, 2) detailne vyhodnotiť všetky jej predmety činností, 3) vrátiť výstup výhradne v štruktúrovanom HTML podľa nižšie definovaného formátu.

    Pravidlá analýzy: Pre každý jednotlivý predmet podnikania vyhodnoť samostatne podľa nasledujúcich polí: 1. Činnosť (pôvodný text). 2. Rizikový Rating (0–100). Stupnica: 0–25 nízke riziko, 26–50 stredné riziko, 51–75 vysoké riziko, 76–100 kritické riziko. 3. Kľúčové poistné nebezpečenstvo (stručne a odborne, napr. škody na zdraví, veciach, finančná strata, výrobok, environmentálna škoda a pod.). 4. Typ rizika z hľadiska General Liability (vyber najlepší typ: Premises / Operations / Product / Professional / Environmental / Contractual / Property damage to Third Party / Bodily Injury / Financial Loss). 5. Red Flag (ÁNO alebo NIE; ÁNO = trhovo problematické, často vylúčené, vyžaduje vysoké limity alebo špeciálny dotazník). 6. Komentár underwritera (1–3 vety so stručným odborným zdôvodnením ratingu). Pre položky 2–5 používaj výhradne faktické a trhové zdôvodnenie, bez hypotetických konštrukcií.

    Formát výstupu: Vráť výstup výhradne ako čistý HTML (bez tagov html, head, body). Pre rizikové skóre používaj CSS classy: risk-score-low, risk-score-medium, risk-score-high, risk-score-critical. Klasifikácia: 0–25 risk-score-low, 26–50 risk-score-medium, 51–75 risk-score-high, 76–100 risk-score-critical.

    Záverečná sekcia (po analýze činností): Vygeneruj sekcie: Celkové Skóre Rizika Firmy (priemer ratingov všetkých činností + slovná interpretácia nízke/stredné/vysoké/kritické). Kritické Klauzuly & Výluky (zahrň len relevantné položky podľa slovenskej praxe, napr. veci vnesené a odložené, cudzie hnuteľné veci, vadný výrobok/product liability, environmentálna zodpovednosť, čisté finančné škody, vlastníctvo nehnuteľností, škody spôsobené subdodávateľmi a podobne – doplň len reálne relevantné). Cross-Sell Tipy (navrhni doplnkové poistné produkty + stručné odôvodnenie, napr. profesná zodpovednosť, produktová zodpovednosť, environmentálne poistenie, kyber, majetok, CAR/EAR a ďalšie). Doplňujúce Otázky pre Klienta (formuluj konkrétne otázky relevantné k posúdeniu rizika; musia znieť ako z reálnej komunikácie makléra s underwriterom, nesmú byť všeobecné alebo generické).
    Výstupné pravidlo: ODPOVEĎ VRÁŤ VŽDY A VÝHRADNE AKO ČISTÝ HTML KÓD. Bez vysvetľovaní, bez komentárov, bez markdownu, bez nadbytočného textu.
    Input: Analýza predmetov činnosti (prepis z ORSR): {st.session_state.user_input}
    Analýza predmetov činnosti (prepis z ORSR):
    {st.session_state.user_input}
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
