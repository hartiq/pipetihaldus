import streamlit as st

# --- TURVALISUSE KONTROLL ---
def check_password():
    """Tagastab True, kui kasutaja on sisestanud õige parooli."""
    def password_entered():
        if st.session_state["password"] == st.secrets["password"]:
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # Eemaldame parooli sessioonist
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        # Näitame sisselogimise akent
        st.text_input("Parool", type="password", on_change=password_entered, key="password")
        return False
    elif not st.session_state["password_correct"]:
        # Vale parooli korral näitame uuesti sisestust ja viga
        st.text_input("Parool", type="password", on_change=password_entered, key="password")
        st.error("❌ Vale parool")
        return False
    else:
        # Parool on õige
        return True

if not check_password():
    st.stop()  # Peatame rakenduse laadimise siinkohal
# --- TURVALISUSE LÕPP ---

# Siit edasi läheb sinu tavaline rakenduse kood...
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

def update_full_entry(row_id, klient, kogus, kontakt, email, tel):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""UPDATE pipetid SET klient=?, kogus=?, kontaktisik=?, email=?, telefon=? 
                 WHERE id=?""", (klient, kogus, kontakt, email, tel, row_id))
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

# 3. KÜLGMENÜÜ: LISAMINE
with st.sidebar:
    st.header("Lisa uus töö")
    
    if not data.empty:
        kliendid_info = data.sort_values('id').drop_duplicates('klient', keep='last').set_index('klient')
        olemasolevad_nimed = sorted(data['klient'].unique().tolist())
    else:
        kliendid_info = pd.DataFrame()
        olemasolevad_nimed = []

    valikud = ["+ Lisa uus..."] + olemasolevad_nimed
    
    # Kasutame key-d, et Streamlit hoiaks olekut
    valitud_klient = st.selectbox("Vali klient või otsi", valikud, key="client_select")
    
    sisestatud_nimi = ""
    default_kontakt, default_email, default_tel = "", "", ""

    if valitud_klient == "+ Lisa uus...":
        # NB! Me ei muuda seda väljaspool, vaid laseme vormil endal puhastuda
        sisestatud_nimi = st.text_input("Uue kliendi nimi", key="new_client_name_input")
    else:
        sisestatud_nimi = valitud_klient
        if valitud_klient in kliendid_info.index:
            default_kontakt = str(kliendid_info.loc[valitud_klient, 'kontaktisik'] or "")
            default_email = str(kliendid_info.loc[valitud_klient, 'email'] or "")
            default_tel = str(kliendid_info.loc[valitud_klient, 'telefon'] or "")

    # Vormi seadistus
    with st.form("lisa_vorm", clear_on_submit=True):
        f_kogus = st.number_input("Kogus", min_value=1, step=1)
        f_saabumine = st.date_input("Saabumise kuupäev", datetime.now())
        
        st.subheader("Kontaktandmed")
        f_kontakt = st.text_input("Kontaktisik", value=default_kontakt)
        f_email = st.text_input("Email", value=default_email)
        f_tel = st.text_input("Telefon", value=default_tel)
        
        # Salvestamise nupp
        submitted = st.form_submit_button("Salvesta")
        
        if submitted:
            if sisestatud_nimi and sisestatud_nimi != "":
                add_entry(sisestatud_nimi, f_kogus, f_saabumine.strftime("%d.%m.%Y"), f_kontakt, f_email, f_tel)
                st.success(f"Salvestatud: {sisestatud_nimi}")
                # Selle asemel et session_state'i torkida, teeme lihtsalt rerun'i
                # clear_on_submit=True puhastab vormisisesed väljad automaatselt
                st.rerun()
            else:
                st.error("Kliendi nimi on puudu!")

# 4. TABELID
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
                    ('saabunud_kalibr', c5, "Kalibreeritud"), ('teavitus', c6, "Teavitatud"), 
                    ('valjastatud', c7, "Väljastatud/saadetud")]

            for field, col, label in btns:
                with col:
                    if not row[field]:
                        if st.button(label, key=f"{field}_{row['id']}"):
                            update_field(row['id'], field, now_str)
                            st.rerun()
                    else:
                        st.caption(f"✅ {row[field]}")

            with c8:
                edit_col, del_col = st.columns(2)
                if edit_col.button("📝", key=f"ed_{row['id']}"):
                    st.session_state[f"edit_mode_{row['id']}"] = True
                if del_col.button("🗑️", key=f"del_{row['id']}"):
                    delete_entry(row['id'])
                    st.rerun()

            if st.session_state.get(f"edit_mode_{row['id']}", False):
                with st.form(f"edit_form_{row['id']}"):
                    e_klient = st.text_input("Klient", value=row['klient'])
                    e_kogus = st.number_input("Kogus", value=row['kogus'])
                    e_kontakt = st.text_input("Kontaktisik", value=row['kontaktisik'])
                    e_email = st.text_input("Email", value=row['email'])
                    e_tel = st.text_input("Telefon", value=row['telefon'])
                    if st.form_submit_button("Uuenda"):
                        update_full_entry(row['id'], e_klient, e_kogus, e_kontakt, e_email, e_tel)
                        st.session_state[f"edit_mode_{row['id']}"] = False
                        st.rerun()
            st.divider()

with tab1:
    aktiivsed = data[data['valjastatud'] == ""]
    if aktiivsed.empty: st.info("Aktiivseid töid pole.")
    else: draw_rows(aktiivsed)

with tab2:
    ajalugu = data[data['valjastatud'] != ""]
    if ajalugu.empty: st.info("Ajalugu on tühi.")
    else: draw_rows(ajalugu)

# 5. EKSPORT
if not data.empty:
    csv = data.to_csv(index=False).encode('utf-8-sig')
    st.sidebar.divider()
    st.sidebar.download_button("Laadi CSV alla", csv, "pipetid_andmed.csv", "text/csv")

