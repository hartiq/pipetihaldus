import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# Rakenduse seadistus
st.set_page_config(page_title="Pipettide seire", layout="wide")
st.title("🧪 Pipettide kalibreerimise ühistabel")

# Loo ühendus Google Sheetsiga
# URL asenda enda tabeli lingiga või lisa see hiljem seadetesse
url = "https://docs.google.com/spreadsheets/d/17tcKGDEh83opzgkTunwTVHx1duszoEXkbf-5wn3c3Rg/edit?usp=sharing"
conn = st.connection("gsheets", type=GSheetsConnection)

# Funktsioon andmete lugemiseks
def get_data():
    return conn.read(spreadsheet=url, usecols=list(range(9)))

data = get_data()

# --- Uue kliendi lisamine ---
with st.expander("➕ Lisa uus saadetis"):
    with st.form("lisa_vorm"):
        klient = st.text_input("Klient")
        kogus = st.number_input("Kogus", min_value=1)
        saabumine = st.date_input("Saabumise kp", datetime.now())
        submit = st.form_submit_button("Salvesta tabelisse")
        
        if submit and klient:
            # Arvutame uue ID
            uue_id = int(data["ID"].max()) + 1 if not data.empty else 1
            uus_rida = pd.DataFrame([{
                "ID": uue_id,
                "Klient": klient,
                "Kogus": kogus,
                "Saabumise kp": saabumine.strftime("%d.%m.%Y"),
                "Kalibreerijale saadetud": "",
                "Kalibreerijal käes": "",
                "Kalibreerijalt saabunud": "",
                "Kliendi teavitus": "",
                "Kliendile saadetud / Ära antud": ""
            }])
            updated_df = pd.concat([data, uus_rida], ignore_index=True)
            conn.update(spreadsheet=url, data=updated_df)
            st.success("Andmed salvestatud!")
            st.rerun()

# --- Tabeli kuvamine ja muutmine ---
st.subheader("Tööde staatus")

for index, row in data.iterrows():
    with st.container():
        c1, c2, c3, c4, c5, c6, c7 = st.columns([1.5, 0.8, 1.2, 1.2, 1.2, 1.2, 1.2])
        
        c1.write(f"**{row['Klient']}**")
        c2.write(f"{row['Kogus']} tk")
        
        # Funktsioon kellaaja märgistamiseks
        def update_cell(col_name, idx):
            data.at[idx, col_name] = datetime.now().strftime("%d.%m.%Y")
            conn.update(spreadsheet=url, data=data)
            st.rerun()

        # Nupud/Staatused
        with c3:
            if not row['Kalibreerijale saadetud']:
                if st.button("Saada", key=f"s1_{index}"): update_cell('Kalibreerijale saadetud', index)
            else: st.caption(f"Saadetud: {row['Kalibreerijale saadetud']}")

        with c4:
            if not row['Kalibreerijal käes']:
                if st.button("Käes", key=f"s2_{index}"): update_cell('Kalibreerijal käes', index)
            else: st.caption(f"Käes: {row['Kalibreerijal käes']}")

        with c5:
            if not row['Kalibreerijalt saabunud']:
                if st.button("Sabus", key=f"s3_{index}"): update_cell('Kalibreerijalt saabunud', index)
            else: st.caption(f"Sabus: {row['Kalibreerijalt saabunud']}")

        with c6:
            if not row['Kliendi teavitus']:
                if st.button("Teavita", key=f"s4_{index}"): update_cell('Kliendi teavitus', index)
            else: st.caption(f"Teavitatud: {row['Kliendi teavitus']}")

        with c7:
            if not row['Kliendile saadetud / Ära antud']:
                if st.button("Väljasta", key=f"s5_{index}"): update_cell('Kliendile saadetud / Ära antud', index)
            else: st.caption(f"Väljastatud: {row['Kliendile saadetud / Ära antud']}")
        
        st.divider()