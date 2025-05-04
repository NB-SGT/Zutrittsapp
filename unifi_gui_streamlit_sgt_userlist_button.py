import streamlit as st
import requests
import time
import urllib3
from fpdf import FPDF

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

API_TOKEN = "QS5JL7IR7qcSwG5JMnXM2A"
CONSOLE_IP = "192.168.1.1"

HEADERS = {
    "Authorization": f"Bearer {API_TOKEN}",
    "Content-Type": "application/json",
    "Accept": "application/json"
}

def benutzer_erstellen(vorname, nachname, email, telefon, mitarbeiternummer, alias, kfz):
    url = f"https://{CONSOLE_IP}:12445/api/v1/developer/users"
    daten = {
        "first_name": vorname,
        "last_name": nachname,
        "user_email": email,
        "phone": telefon,
        "employee_number": mitarbeiternummer,
        "alias": alias,
        "note": f"KFZ: {kfz}",
        "onboard_time": int(time.time())
    }
    response = requests.post(url, json=daten, headers=HEADERS, verify=False)
    response.raise_for_status()
    return response.json()["data"]["id"]

def pin_setzen(user_id, pin_code):
    url = f"https://{CONSOLE_IP}:12445/api/v1/developer/users/{user_id}/pin_codes"
    daten = {"pin_code": pin_code}
    response = requests.put(url, json=daten, headers=HEADERS, verify=False)
    response.raise_for_status()
    return response.json()

def pdf_erstellen(daten):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Benutzerregistrierung", ln=True, align="C")
    for key, value in daten.items():
        pdf.cell(200, 10, txt=f"{key}: {value}", ln=True)
    return pdf.output(dest='S').encode('latin-1')


# === Styling einfügen ===
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Audiowide&display=swap');

    html, body, [class*="css"]  {
        background-color: #4169E1;
        color: white;
        font-family: 'Audiowide', cursive;
    }

    .stButton > button {
        background-color: #ffffff;
        color: #4169E1;
        border-radius: 8px;
        padding: 0.4em 1em;
        font-weight: bold;
    }

    .stDownloadButton > button {
        background-color: #ffffff;
        color: #4169E1;
        border-radius: 8px;
        padding: 0.4em 1em;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)


# === Stil + Logo ===
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Audiowide&display=swap');

    html, body, [class*="css"]  {
        background-color: #4169E1;
        color: white;
        font-family: 'Audiowide', cursive;
    }

    .stButton > button, .stDownloadButton > button {
        background-color: #ffffff;
        color: #4169E1;
        border-radius: 8px;
        padding: 0.4em 1em;
        font-weight: bold;
    }

    .form-box {
        background-color: rgba(255, 255, 255, 0.05);
        border-radius: 16px;
        padding: 2rem;
        margin: 2rem auto;
        width: 100%;
        max-width: 600px;
        box-shadow: 0px 0px 20px rgba(0,0,0,0.2);
    }

    img.logo {
        display: block;
        margin-left: auto;
        margin-right: auto;
        width: 80%;
        max-width: 500px;
        margin-top: 1rem;
        margin-bottom: 2rem;
    }
    </style>
""", unsafe_allow_html=True)

# === Logo anzeigen ===
from PIL import Image
logo = Image.open("logo.png")
st.image(logo, output_format="PNG", width=600)

# === Formular als Karte ===
st.markdown('<div class="form-box">', unsafe_allow_html=True)

st.title('SGT Zutrittsmanager – Person anlegen')

if "form_reset" not in st.session_state:
    st.session_state.form_reset = False

with st.form("benutzer_formular", clear_on_submit=st.session_state.form_reset):
    vorname = st.text_input("Vorname")
    nachname = st.text_input("Nachname")
    email = st.text_input("E-Mail")
    telefon = st.text_input("Telefon")
    mitarbeiternummer = st.text_input("Mitarbeiternummer")
    alias = st.text_input("Alias")
    kfz = st.text_input("KFZ-Kennzeichen")
    pin_code = st.text_input("PIN-Code", type="password")

    col1, col2 = st.columns([1, 1])
    with col1:
        submitted = st.form_submit_button("Benutzer anlegen")
    with col2:
        reset = st.form_submit_button("Eingaben löschen")
        if reset:
            st.session_state.form_reset = True

if submitted:
    try:
        user_id = benutzer_erstellen(vorname, nachname, email, telefon, mitarbeiternummer, alias, kfz)
        pin_setzen(user_id, pin_code)
        st.success(f"Benutzer {vorname} {nachname} erfolgreich angelegt!")

        daten = {
            "Vorname": vorname,
            "Nachname": nachname,
            "E-Mail": email,
            "Telefon": telefon,
            "Mitarbeiternummer": mitarbeiternummer,
            "Alias": alias,
            "KFZ": kfz,
            "Benutzer-ID": user_id
        }
        pdf_bytes = pdf_erstellen(daten)
        st.download_button("📄 PDF herunterladen", data=pdf_bytes, file_name=f"{vorname}_{nachname}_Zugang.pdf")

    except Exception as e:
        st.error(f"Fehler: {e}")
st.markdown('</div>', unsafe_allow_html=True)

# Benutzerliste anzeigen (nur nach Klick)
if st.button("📋 Alle Benutzer anzeigen"):
    try:
        response = requests.get(f"https://{CONSOLE_IP}:12445/api/v1/developer/users", headers=HEADERS, verify=False)
        response.raise_for_status()
        benutzer_liste = response.json().get("data", [])
        if benutzer_liste:
            tabellen_daten = [
                {
                    "Vorname": b.get("first_name", ""),
                    "Nachname": b.get("last_name", ""),
                    "Alias": b.get("alias", ""),
                    "E-Mail": b.get("user_email", ""),
                    "Mitarbeiter-ID": b.get("employee_number", "")
                }
                for b in benutzer_liste
            ]
            st.subheader("Alle Benutzer")
            st.table(tabellen_daten)
        else:
            st.info("Keine Benutzer gefunden.")
    except Exception as e:
        st.error(f"Fehler beim Abrufen der Benutzer: {e}")