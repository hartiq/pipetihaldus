import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# 1. RAKENDUSE SEADISTUS
st.set_page_config(page_title="Pipettide seire", layout="wide")
st.title("🧪 Pipettide kalibreerimise haldus")

# Sinu Google Sheetsi link
SHEET_URL = "https://docs.google.com/spreadsheets/d/17tcKGDEh83opzgkTunwTVHx1duszoEXkbf-5wn3c3Rg/edit?usp=sharing"

# 2. ÜHENDUSE LOOMINE
conn = st.connection("gsheets", type=GSheetsConnection)

def get_data():
    # Loeme andmed ja puhastame tulpade nimed tühikutest
    df = conn.read(spreadsheet=SHEET_URL)
    df.columns = df.columns.str.strip()
    return df

try:
    data = get_data()
except Exception as e:
    st.error(f"Viga andmete lugemisel: {e}")
    st.stop()

# Määrame täpsed tulpade nimed vastavalt sinu tabelile
COL_ID = "ID"
COL_KLIENT = "Klient"
COL_KOGUS = "Kogus"
COL_SAABUMINE = "Saabumise kp"
COL_SAADETUD = "Kalibreerijale saadetud"
COL_KAES = "Kalibreerijal käes"
COL_SABUNUD = "Kalibreerijalt saabunud"
COL_TEAVITUS = "Kliendi teavitus"
COL_VALJASTATUD = "Kliendile saadetud / Ära antud"

# 3. UUE KLIENDI LISAMINE
with st.sidebar:
    st.header("Lisa uus töö")
    with st.form("lisa_vorm", clear_on_submit=True):
        uus_klient = st.text_input("Kliendi nimi")
        uus_kogus = st.number_input("Kogus", min_value=1, step=1)
        uus_saabumine = st.date_input("Saabumise kuupäev", datetime.now())
        lisa_nupp = st.form_submit_button("Salvesta tabelisse")

        if lisa_nupp and uus_klient:
            # Arvutame uue ID (viimane ID + 1)
            uue_id = int(data[COL_ID].max()) + 1 if not data.empty and COL_ID in data else 1
            
            uus_rida = pd.DataFrame([{
                COL_ID: uue_id,
                COL_KLIENT: uus_klient,
                COL_KOGUS: uus_kogus,
                COL_SAABUMINE: uus_saabumine.strftime("%d.%m.%Y"),
                COL_SAADETUD: "",
                COL_KAES: "",
                COL_SABUNUD: "",
                COL_TEAVITUS: "",
                COL_VALJASTATUD: ""
            }])
            
            updated_df = pd.concat([data, uus_rida], ignore_index=True)
            conn.update(spreadsheet=SHEET_URL, data=updated_df)
            st.success(f"Lisatud: {uus_klient}")
            st.rerun()

# 4. TABELI KUVAMINE JA MUUTMINE
st.subheader("Aktiivsed tööd")

# Abifunktsioon tühja lahtri kontrolliks (hoiab ära vea, kui lahter on tühi või NaN)
def is_empty(val):
    return pd.isna(val) or str(val).strip() == "" or str(val).strip() == "-" or str(val).strip() == "nan"

if not data.empty:
    for index, row in data.iterrows():
        # Kui töö on juba täielikult väljastatud, võime selle soovi korral peita või kuvada hallina
        # Hetkel kuvame kõik
        
        with st.container():
            c1, c2, c3, c4, c5, c6, c7 = st.columns([1.5, 0.7, 1.3, 1.3, 1.3, 1.3, 1.5])
            
            c1.write(f"**{row[COL_KLIENT]}**")
            c2.write(f"{row[COL_KOGUS]} tk")
            
            # Funk
