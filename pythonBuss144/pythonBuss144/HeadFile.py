import streamlit as st
import pandas as pd
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

from Bus.Bus import Buss144, Buss144Fruangen
from Train.Train import Train

# Initiera boards
buss = Buss144()
buss_fruangen = Buss144Fruangen()
tag = Train()

STOPS = [buss, buss_fruangen, tag]

# Autorefresh varje sekund
st_autorefresh(interval=1000, key="refresh")

# Titel
st.markdown("## 🚌🚆 Live-tavla: Buss + Tåg")
st.caption(f"Senast uppdaterad: {datetime.now().strftime('%H:%M:%S')}")

# Lagra senaste API-data i session_state
if "departures" not in st.session_state:
    st.session_state.departures = {}
    st.session_state.last_fetch = {}

def fetch_departures(stop):
    # Hämta från klassen
    return stop.fetch()

# Bygg tabeller för varje stop
for stop in STOPS:
    now = datetime.now()

    # Hämta nya tider var 30:e sekund
    if (
        stop.name not in st.session_state.last_fetch
        or (now - st.session_state.last_fetch[stop.name]).total_seconds() > 30
    ):
        st.session_state.departures[stop.name] = fetch_departures(stop)
        st.session_state.last_fetch[stop.name] = now

    departures = st.session_state.departures.get(stop.name, [])

    # Bygg en DataFrame
    rows = []
    for line_name, dep_dt, rt_dt, countdown_base, delay_text in departures:
        countdown = countdown_base - now
        total_sec = int(countdown.total_seconds())
        if total_sec < 0:
            continue

        minutes = total_sec // 60
        seconds = total_sec % 60
        countdown_str = "Avgår nu" if (minutes == 0 and seconds == 0) else f"{minutes:02d}:{seconds:02d}"

        rows.append({
            "Linje": line_name,
            "Planerad": dep_dt.strftime("%H:%M:%S"),
            "Realtid": rt_dt.strftime("%H:%M:%S"),
            "Nedräkning": countdown_str,
            "Försening": f"⚠️ {delay_text}" if delay_text else ""
        })

    df = pd.DataFrame(rows)

    # Snygg rubrik
    st.markdown(f"### {stop.name}")

    if not df.empty:
        # Visa tabellen utan index (drop=True tar bort siffrorna 0,1,2,3…)
        st.table(df.reset_index(drop=True))
    else:
        st.info("Inga avgångar just nu.")
