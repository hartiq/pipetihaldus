# Funktsioon andmete lugemiseks ja tulpade puhastamiseks
def get_data():
    df = conn.read(spreadsheet=url)
    # Eemaldame tulpade nimedest üleliigsed tühikud algusest ja lõpust
    df.columns = df.columns.str.strip()
    return df

data = get_data()

# --- Tabeli kuvamine ja muutmine ---
st.subheader("Tööde staatus")

# Määrame täpsed tulpade nimed, mida koodist otsime
# NB! Veendu, et Google Sheetsis on need TÄPSELT nii
col_saadetud = "Kalibreerijale saadetud"
col_kaes = "Kalibreerijal käes"
col_sabunud = "Kalibreerijalt saabunud"
col_teavitus = "Kliendi teavitus"
col_valjastatud = "Kliendile saadetud / Ära antud"

for index, row in data.iterrows():
    with st.container():
        c1, c2, c3, c4, c5, c6, c7 = st.columns([1.5, 0.8, 1.2, 1.2, 1.2, 1.2, 1.2])
        
        c1.write(f"**{row['Klient']}**")
        c2.write(f"{row['Kogus']} tk")
        
        def update_cell(col_name, idx):
            data.at[idx, col_name] = datetime.now().strftime("%d.%m.%Y")
            conn.update(spreadsheet=url, data=data)
            st.rerun()

        # Kasutame .get() meetodit või kontrollime sisu turvaliselt
        with c3:
            val = str(row[col_saadetud]) if col_saadetud in row else ""
            if val == "" or val == "nan" or val == "-":
                if st.button("Saada", key=f"s1_{index}"): update_cell(col_saadetud, index)
            else: st.caption(f"Saadetud: {val}")

        with c4:
            val = str(row[col_kaes]) if col_kaes in row else ""
            if val == "" or val == "nan" or val == "-":
                if st.button("Käes", key=f"s2_{index}"): update_cell(col_kaes, index)
            else: st.caption(f"Käes: {val}")

        with c5:
            val = str(row[col_sabunud]) if col_sabunud in row else ""
            if val == "" or val == "nan" or val == "-":
                if st.button("Sabus", key=f"s3_{index}"): update_cell(col_sabunud, index)
            else: st.caption(f"Sabus: {val}")

        with c6:
            val = str(row[col_teavitus']) if col_teavitus in row else ""
            if val == "" or val == "nan" or val == "-":
                if st.button("Teavita", key=f"s4_{index}"): update_cell(col_teavitus, index)
            else: st.caption(f"Teavitatud: {val}")

        with c7:
            # See on see koht, mis vea andis
            val = str(row[col_valjastatud]) if col_valjastatud in row else ""
            if val == "" or val == "nan" or val == "-":
                if st.button("Väljasta", key=f"s5_{index}"): update_cell(col_valjastatud, index)
            else: st.caption(f"Väljastatud: {val}")
        
        st.divider()
