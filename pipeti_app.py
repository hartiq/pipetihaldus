import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime

# 1. ANDMEBAASI SEADISTUS (SQLite)
DB_FILE = "pipetid_andmed.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS pipetid
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  klient TEXT, 
                  kogus INTEGER, 
                  saabumine TEXT, 
                  saadetud_kalibr TEXT, 
                  kaes_kalibr TEXT, 
                  saabunud_kalibr TEXT, 
                  teavitus TEXT, 
                  valjastatud TEXT)''')
    conn.commit()
    conn.close()

def load_data():
    conn = sqlite3.connect(DB_FILE)
    df = pd.read_sql_query("SELECT * FROM pipetid ORDER BY id DESC", conn)
    conn.close()
    return df

def add_entry(klient, kogus, saabumine):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("INSERT INTO pipetid (klient, kogus, saabumine, saadetud_kalibr, kaes_kalibr, saabunud_kalibr, teavitus, valjastatud) VALUES (?, ?, ?, '', '', '', '', '')",
              (klient, kogus, saabumine))
    conn.commit()
    conn.close()

def update_field(row_id, column, value):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute(f"UPDATE pipetid SET {column} = ? WHERE id = ?", (value, row_id))
    conn.commit()
    conn.close()

# 2. RAKENDUSE LIIDES
st.set_page_config(page_title="Pipettide seire", layout="wide")
init_db()

st.title("🧪 Pipettide kalibreerimise sisesüsteem")
st.info("Andmed salvestatakse rakenduse siseandmebaasi.")

# Külgmenüü uue töö lisamiseks
with st.sidebar:
    st.header("Lisa uus töö")
    with st.form("lisa_vorm", clear_on_submit=True):
        klient = st.text_input("Kliendi nimi")
        kogus = st.number_input("Kogus", min_value=1, step=1)
        saabumine = st.date_input("Saabumise kuupäev", datetime.now())
        submit = st.form_submit_button("Salvesta")
        
        if submit and klient:
            add_entry(klient, kogus, saabumine.strftime("%d.%m.%Y"))
            st.success(f"Lisatud: {klient}")
            st.rerun()

# 3. ANDMETE KUVAMINE
data = load_data()

def is_empty(val):
    return val == "" or val is None

if not data.empty:
    for index, row in data.iterrows():
        with st.container():
            c1, c2, c3, c4, c5, c6, c7 = st.columns([1.5, 0.6, 1.2, 1.2, 1.2, 1.2, 1.2])
            
            c1.write(f"**{row['klient']}**")
            c2.write(f"{row['kogus']} tk")
            
            # Nuppude funktsionaalsus
            now_str = datetime.now().strftime("%d.%m.%Y")
            
            with c3:
                if is_empty(row['saadetud_kalibr']):
                    if st.button("Saadetud", key=f"btn1_{row['id']}"):
                        update_field(row['id'], "saadetud_kalibr", now_str)
                        st.rerun()
                else: st.caption(f"📤 {row['saadetud_kalibr']}")

            with c4:
                if is_empty(row['kaes_kalibr']):
                    if st.button("Saabus Tallinnasse", key=f"btn2_{row['id']}"):
                        update_field(row['id'], "kaes_kalibr", now_str)
                        st.rerun()
                else: st.caption(f"🔧 {row['kaes_kalibr']}")

            with c5:
                if is_empty(row['saabunud_kalibr']):
                    if st.button("Tagasi Tartus", key=f"btn3_{row['id']}"):
                        update_field(row['id'], "saabunud_kalibr", now_str)
                        st.rerun()
                else: st.caption(f"🏠 {row['saabunud_kalibr']}")

            with c6:
                if is_empty(row['teavitus']):
                    if st.button("Teavitatud", key=f"btn4_{row['id']}"):
                        update_field(row['id'], "teavitus", now_str)
                        st.rerun()
                else: st.caption(f"📧 {row['teavitus']}")

            with c7:
                if is_empty(row['valjastatud']):
                    if st.button("Väljastatud", key=f"btn5_{row['id']}"):
                        update_field(row['id'], "valjastatud", now_str)
                        st.rerun()
                else: st.info(f"✅ {row['valjastatud']}")
            
            st.divider()
else:
    st.write("Tabel on tühi. Lisa esimene klient vasakult menüüst.")

# 4. EKSPORDI VÕIMALUS (Varukoopiaks)
if not data.empty:
    st.sidebar.divider()
    csv = data.to_csv(index=False).encode('utf-8-sig')
    st.sidebar.download_button("Laadi andmed Excelisse (CSV)", csv, "pipetid_export.csv", "text/csv")

