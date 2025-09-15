import streamlit as st
import pandas as pd
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

from Bus.Bus import Buss144, Buss144Fruangen
from Train.Train import Train

# autorefresh varje sekund
st_autorefresh(interval=1000, limit=None, key="refresh")

# Initiera alla boards
buss = Buss144()
buss_fruangen = Buss144Fruangen()
tag = Train()

STOPS = [buss, buss_fruangen, tag]

st.set_page_config(page_title="Live-tavla Buss + Tåg", layout="centered")

st.title("🚌🚉 Live-tavla: Buss + Tåg")

st.caption(f"Senast uppdaterad: {datetime.now().strftime('%H:%M:%S')}")

for stop in STOPS:
    st.subheader(stop.name)

    departures = stop.fetch()
    rows = []

    for line_name, dep_dt, rt_dt, countdown_base, delay_text in departures:
        countdown = countdown_base - datetime.now()
        total_sec = int(countdown.total_seconds())
        if total_sec < 0:
            continue

        hours = total_sec // 3600
        minutes = (total_sec % 3600) // 60
        seconds = total_sec % 60

        if hours > 0:
            countdown_str = f"{hours}:{minutes:02d}:{seconds:02d}"
        elif minutes == 0 and seconds == 0:
            countdown_str = "Avgår nu"
        else:
            countdown_str = f"{minutes:02d}:{seconds:02d}"

        rows.append({
            "Linje": line_name,
            "Planerad": dep_dt.strftime("%H:%M:%S"),
            "Nedräkning": countdown_str
        })

    if rows:
        df = pd.DataFrame(rows)
        st.table(df)
    else:
        st.info("Inga avgångar just nu")
