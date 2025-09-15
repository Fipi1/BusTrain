import streamlit as st
import pandas as pd
from datetime import datetime
from Bus.Bus import Buss144, Buss144Fruangen
from Train.Train import Train

# Initiera alla boards
buss = Buss144()
buss_fruangen = Buss144Fruangen()
tag = Train()

STOPS = [buss, buss_fruangen, tag]

st.set_page_config(page_title="Live-tavla: Buss + Tåg", layout="centered")

# Titel
st.markdown("## 🚌🚆 Live-tavla: Buss + Tåg")
st.caption(f"Senast uppdaterad: {datetime.now().strftime('%H:%M:%S')}")

for stop in STOPS:
    data = stop.fetch()

    rows = []
    for line_name, dep_dt, rt_dt, countdown_base, delay_text in data:
        now = datetime.now()
        countdown = countdown_base - now
        total_sec = int(countdown.total_seconds())

        if total_sec < 0:
            continue

        minutes = total_sec // 60
        seconds = total_sec % 60

        if minutes == 0 and seconds == 0:
            countdown_str = "Avgår nu"
        else:
            countdown_str = f"{minutes:02d}:{seconds:02d}"

        rows.append({
            "Linje": line_name,
            "Planerad": dep_dt.strftime("%H:%M:%S"),
            "Nedräkning": countdown_str
        })

    st.subheader(stop.name)
    if rows:
        df = pd.DataFrame(rows)
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("Inga avgångar hittades just nu.")
