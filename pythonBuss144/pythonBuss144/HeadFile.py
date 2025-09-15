import requests
import streamlit as st
from datetime import datetime
import json

# Ladda mapping från config.json
with open("pythonBuss144/pythonBuss144/config.json", encoding="utf-8") as f:
    config = json.load(f)

STATION_NAME_MAP = config["STATION_NAME_MAP"]

# API-nyckel från Streamlit secrets
API_KEY = st.secrets["API_KEY"]

# ======================
# Funktion för att hämta avgångar
# ======================
def fetch_departures(stop_id, line_id=None, filter_list=None):
    url = f"https://api.resrobot.se/v2.1/departureBoard?accessId={API_KEY}&id={stop_id}&format=json&maxJourneys=10"
    if line_id:
        url += f"&lineId={line_id}"

    resp = requests.get(url)
    data = resp.json()

    result = []
    for dep in data.get("Departure", []):
        direction = dep["direction"]

        # Filtrera på riktning
        if filter_list and not any(f in direction for f in filter_list):
            continue

        dep_date = dep.get("date")
        dep_time = dep.get("time")
        dep_dt = datetime.strptime(f"{dep_date} {dep_time}", "%Y-%m-%d %H:%M:%S")

        rt_date = dep.get("rtDate", dep_date)
        rt_time = dep.get("rtTime", dep_time)
        rt_dt = datetime.strptime(f"{rt_date} {rt_time}", "%Y-%m-%d %H:%M:%S")

        delay = int((rt_dt - dep_dt).total_seconds() // 60)
        delay_text = f"⚠️ +{delay} min" if delay > 0 else ""

        countdown = rt_dt - datetime.now()
        minutes = int(countdown.total_seconds() // 60)
        seconds = int(countdown.total_seconds() % 60)

        countdown_str = "Avgår nu" if minutes == 0 and seconds == 0 else f"{minutes:02d}:{seconds:02d}"

        line_display = f"{dep['name']} → {STATION_NAME_MAP.get(direction, direction)}"
        result.append((line_display, dep_time, rt_time, countdown_str, delay_text))

    return result


# ======================
# Streamlit GUI
# ======================
st.set_page_config(page_title="Live-tavla: Buss + Tåg", layout="centered")

st.title("🚌🚆 Live-tavla: Buss + Tåg")
st.write(f"Senast uppdaterad: {datetime.now().strftime('%H:%M:%S')}")

# Buss 144 från Myrvägen → Gullmarsplan
st.subheader("Buss 144 → Gullmarsplan (Myrvägen)")
buss_data = fetch_departures("740065500", line_id="1275014400001", filter_list=["Gullmarsplan"])
st.table(buss_data)

# Buss 144 från Älvsjö → Fruängen (efter kl 16)
if datetime.now().hour >= 16:
    st.subheader("Buss 144 → Fruängen (Älvsjö station)")
    buss_fru_data = fetch_departures("740000789", line_id="1275014400001", filter_list=["Fruängen"])
    st.table(buss_fru_data)

# Pendeltåg från Älvsjö → Stockholm C
st.subheader("Pendeltåg → Stockholm C (Älvsjö)")
train_data = fetch_departures("740000789", filter_list=["Uppsala", "Märsta", "Bålsta", "Stockholm City", "Stockholm Central"])
st.table(train_data)
