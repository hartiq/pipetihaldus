import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime

# 1. ANDMEBAASI HALDUS
DB_FILE = "pipetid_v2.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    # Lisatud uued väljad: kontaktisik, email, telefon
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

def delete_entry(row_id):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("DELETE FROM pipetid WHERE id = ?", (row_id,))
    conn.commit()
    conn.close()

def update_field(row_id, column, value):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute(f"UPDATE pipetid SET {column} = ? WHERE id = ?", (value, row_id))
    conn.commit()
    conn.close()

# 2. RAKENDUSE LIIDES
st.set_page_config(page_title="Pipettide seire PRO", layout="wide")
init_db()

st.title("🧪 Pipettide kalibreerimise süsteem")

data = load_data()

# 3. NUTIKAS LISAMISVORM (Sidebar)
with st.sidebar:
    st.header("Lisa uus töö")
    
    # Leiame unikaalsed kliendid ja nende andmed automaatseks täitmiseks
    if not data.empty:
        kliendid_info = data.drop_duplicates('klient').set_index('klient')
        olemasolevad_nimed = sorted(data['klient'].unique().tolist())
    else:
        kliendid_info = pd.DataFrame()
        olemasolevad_nimed = []

    # Valik või uus nimi
    valitud_klient = st.selectbox("Vali klient või trüki uus", [""] + olemasolevad_nimed + ["+ Lisa uus..."])
    
    if valitud_klient == "+ Lisa uus...":
        sisestatud_nimi = st.text_input("Uue kliendi nimi")
    else:
        sisestatud_nimi = valitud_klient

    # Automaatne andmete täitmine, kui klient on varem olnud
    default_kontakt = ""
    default_email = ""
    default_tel = ""
    
    if sisestatud_nimi in kliendid_info.index:
        default_kontakt = kliendid_info.loc[sisestatud_nimi, 'kontaktisik']
        default_email = kliendid_info.loc[sisestatud_nimi, 'email']
        default_tel = kliendid_info.loc[sisestatud_nimi, 'telefon']

    with st.form("lisa_vorm", clear_on_submit=True):
        f_kogus = st.number_input("Kogus", min_value=1, step=1)
        f_saabumine = st.date_input("Saabumise kuupäev", datetime.now())
        
        st.subheader("Kontaktandmed (vabatahtlik)")
        f_kontakt = st.text_input("Kontaktisik", value=default_kontakt)
        f_email = st.text_input("Email", value=default_email)
        f_tel = st.text_input("Telefon", value=default_tel)
        
        submit = st.form_submit_button("Salvesta andmebaasi")
        
        if submit and sisestatud_nimi:
            add_entry(sisestatud_nimi, f_kogus, f_saabumine.strftime("%d.%m.%Y"), f_kontakt, f_email, f_tel)
            st.success(f"Lisatud: {sisestatud_nimi}")
            st.rerun()

# 4. TABELI KUVAMINE
st.subheader("Aktiivsed tööd")

if not data.empty:
    for index, row in data.iterrows():
        with st.container():
            # Tulbad: Klient/Kontakt, Kogus, 5 x Staatus, Kustuta
            c1, c2, c3, c4, c5, c6, c7, c8 = st.columns([1.5, 0.5, 1, 1, 1, 1, 1, 0.5])
            
            with c1:
                st.write(f"**{row['klient']}**")
                if row['kontaktisik']: st.caption(f"👤 {row['kontaktisik']}")
                if row['email']: st.caption(f"📧 {row['email']}")

            c2.write(f"{row['kogus']} tk")
            
            now_str = datetime.now().strftime("%d.%m.%Y")
            
            # Status buttons
            cols = [('saadetud_kalibr', c3, "Saadaetud"), ('kaes_kalibr', c4, "Tallinnas"), 
                    ('saabunud_kalibr', c5, "Kalibreeritud"), ('teavitus', c6, "Teavitatud"), 
                    ('valjastatud', c7, "Väljastatud/Saadetud")]

            for field, col, label in cols:
                with col:
                    if not row[field]:
                        if st.button(label, key=f"{field}_{row['id']}"):
                            update_field(row['id'], field, now_str)
                            st.rerun()
                    else:
                        st.caption(f"✅ {row[field]}")

            # KUSTUTAMISE NUPP
            with c8:
                if st.button("🗑️", key=f"del_{row['id']}", help="Kustuta rida"):
                    delete_entry(row['id'])
                    st.rerun()
            
            st.divider()
else:
    st.info("Andmebaas on tühi.")

# 5. EKSPORT
if not data.empty:
    csv = data.to_csv(index=False).encode('utf-8-sig')
    st.sidebar.download_button("Laadi andmed alla (CSV)", csv, "pipetid_andmebaas.csv", "text/csv")
