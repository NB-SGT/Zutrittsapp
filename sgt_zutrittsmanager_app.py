import streamlit as st
import requests

API_TOKEN = "QS5JL7IR7qcSwG5JMnXM2A"
CONSOLE_IP = "192.168.1.1"
API_BASE_URL = f"https://{CONSOLE_IP}/api/v1"

HEADERS = {
    "Authorization": f"Bearer {API_TOKEN}",
    "Content-Type": "application/json"
}

def benutzer_anlegen(vorname, nachname, email, telefon, pin):
    user_data = {
        "first_name": vorname,
        "last_name": nachname,
        "email": email,
        "phone": telefon
    }

    user_response = requests.post(f"{API_BASE_URL}/users", headers=HEADERS, json=user_data, verify=False)

    if user_response.status_code == 200:
        user_id = user_response.json().get("data", {}).get("_id", "")
        if pin and 4 <= len(pin) <= 8:
            pin_data = {"pin": pin}
            requests.post(f"{API_BASE_URL}/users/{user_id}/pin", headers=HEADERS, json=pin_data, verify=False)
            return True, "(mit PIN)"
        return True, "(ohne PIN)"
    return False, ""

st.set_page_config(page_title="SGT Zutrittsmanager", page_icon="🔐", layout="centered")

st.title("SGT Zutrittsmanager – Person anlegen")

with st.form("benutzer_formular"):
    vorname = st.text_input("Vorname")
    nachname = st.text_input("Nachname")
    email = st.text_input("E-Mail")
    telefon = st.text_input("Telefonnummer")
    pin = st.text_input("PIN-Code", type="password")

    col1, col2 = st.columns(2)
    submit = col1.form_submit_button("Benutzer anlegen")
    reset = col2.form_submit_button("Eingaben löschen")

if submit:
    success, pin_info = benutzer_anlegen(vorname, nachname, email, telefon, pin)
    if success:
        st.success(f"✅ {vorname} {nachname} erfolgreich angelegt {pin_info}.")
    else:
        st.error("❌ Fehler beim Anlegen des Benutzers.")
