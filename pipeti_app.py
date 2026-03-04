import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime

# 1. ANDMEBAASI HALDUS
DB_FILE = "pipetid_v2.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS pipetid
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  klient TEXT, kogus INTEGER, saabumine TEXT, 
                  saadetud_kalibr TEXT, kaes_kalibr TEXT, saabunud_kalibr TEXT, 
                  teavitus TEXT, valjastatud TEXT,
                  kontaktisik TEXT, email TEXT, telefon TEXT)''')
    conn.commit()
    conn.close()

def load_data():
    conn = sqlite3.connect(DB_FILE)
    df = pd.read_sql_query("SELECT * FROM pipetid ORDER BY id DESC", conn)
    conn.close()
    return df

def add_entry(klient, kogus, saabumine, kontakt, email, tel):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""INSERT INTO pipetid 
                 (klient, kogus, saabumine, saadetud_kalibr, kaes_kalibr, saabunud_kalibr, 
                  teavitus, valjastatud, kontaktisik, email, telefon) 
                 VALUES (?, ?, ?, '', '', '', '', '', ?, ?, ?)""",
              (klient, kogus, saabumine, kontakt, email, tel))
    conn.commit()
    conn.close()

def update_field(row_id, column, value):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute(f"UPDATE pipetid SET {column} = ? WHERE id = ?", (value, row_id))
    conn.commit()
    conn.close()

# 2. RAKENDUSE SEADISTUS
st.set_page_config(page_title="Pipettide seire PRO", layout="wide")
init_db()
data = load_data()

# ABIKONTROLL MOBIILILE: Suur märguanne, kui sidebar on peidus
if st.button("➕ AVA SISESTAMISE AKEN (VASAKUL)", use_container_width=True):
    st.info("Kasuta vasakpoolset menüüd andmete sisestamiseks. Mobiilis ava see vasakult ülevalt noolega.")

# 3. KÜLGMENÜÜ: LISAMINE
with st.sidebar:
    st.header("Lisa uus töö")
    
    if not data.empty:
        kliendid_info = data.sort_values('id').drop_duplicates('klient', keep='last').set_index('klient')
        olemasolevad_nimed = sorted(data['klient'].unique().tolist())
    else:
        kliendid_info = pd.DataFrame()
        olemasolevad_nimed = []

    # LAHENDUS: Eraldi märkeruut uue kliendi jaoks, mis ei kao kunagi ära
    lisa_uus_klient = st.checkbox("✨ LISA TÄIESTI UUS KLIENT", value=False)
    
    d_nimi = ""
    d_kontakt, d_email, d_tel = "", "", ""

    if lisa_uus_klient:
        d_nimi = st.text_input("Uue kliendi nimi", key="uus_nimi_manual")
    else:
        # Siin on nüüd ainult olemasolevad, et otsing oleks puhas
        valitud_klient = st.selectbox("Vali olemasolev klient", [""] + olemasolevad_nimed)
        if valitud_klient != "":
            d_nimi = valitud_klient
            if valitud_klient in kliendid_info.index:
                d_kontakt = str(kliendid_info.loc[valitud_klient, 'kontaktisik'] or "")
                d_email = str(kliendid_info.loc[valitud_klient, 'email'] or "")
                d_tel = str(kliendid_info.loc[valitud_klient, 'telefon'] or "")

    with st.form("lisa_vorm", clear_on_submit=True):
        f_kogus = st.number_input("Kogus", min_value=1, step=1)
        f_saabumine = st.date_input("Saabumise kuupäev", datetime.now())
        st.write("---")
        f_kontakt = st.text_input("Kontaktisik", value=d_kontakt)
        f_email = st.text_input("Email", value=d_email)
        f_tel = st.text_input("Telefon", value=d_tel)
        
        if st.form_submit_button("Salvesta andmebaasi"):
            if d_nimi and d_nimi != "":
                add_entry(d_nimi, f_kogus, f_saabumine.strftime("%d.%m.%Y"), f_kontakt, f_email, f_tel)
                st.success(f"Salvestatud!")
                st.rerun()
            else:
                st.error("Kliendi nimi on puudu!")

# 4. TABELID
st.title("🧪 Pipettide kalibreerimise süsteem")
tab1, tab2 = st.tabs(["🚀 Aktiivsed tööd", "📜 Ajalugu"])

def draw_rows(df_subset):
    for index, row in df_subset.iterrows():
        with st.container():
            c1, c2, c3, c4, c5, c6, c7, c8 = st.columns([1.6, 0.5, 1, 1, 1, 1, 1, 0.6])
            with c1:
                st.write(f"**{row['klient']}**")
                st.caption(f"👤 {row['kontaktisik'] or '-'} | 📧 {row['email'] or '-'} | 📞 {row['telefon'] or '-'}")
            c2.write(f"{row['kogus']} tk")
            
            now_str = datetime.now().strftime("%d.%m.%Y")
            btns = [('saadetud_kalibr', c3, "Saadetud"), ('kaes_kalibr', c4, "Tallinnas"), 
                    ('saabunud_kalibr', c5, "Kalibr."), ('teavitus', c6, "Teavitatud"), 
                    ('valjastatud', c7, "Väljastatud")]

            for field, col, label in btns:
                with col:
                    if not row[field]:
                        if st.button(label, key=f"{field}_{row['id']}"):
                            update_field(row['id'], field, now_str)
                            st.rerun()
                    else: st.caption(f"✅ {row[field]}")

            with c8:
                if st.button("🗑️", key=f"del_{row['id']}"):
                    conn = sqlite3.connect(DB_FILE)
                    c = conn.cursor()
                    c.execute("DELETE FROM pipetid WHERE id = ?", (row['id'],))
                    conn.commit()
                    conn.close()
