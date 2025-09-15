import requests
from datetime import datetime
import json
import streamlit as st

API_KEY = st.secrets["API_KEY"]
STATION_NAME_MAP = st.secrets["STATION_NAME_MAP"]


class Train:
    """Pendeltåg mot Stockholm C från Älvsjö"""
    def __init__(self):
        self.name = "Pendeltåg → Stockholm C (Älvsjö)"
        self.stop_id = "740000789"  # Älvsjö station
        self.filter = ["Uppsala", "Märsta", "Bålsta", "Stockholm City", "Stockholm Central"]

    def fetch(self):
        url = (
            f"https://api.resrobot.se/v2.1/departureBoard?"
            f"accessId={API_KEY}&id={self.stop_id}&format=json&maxJourneys=20"
        )
        resp = requests.get(url)
        data = resp.json()

        result = []
        for dep in data.get("Departure", []):
            direction = dep["direction"]
            if not any(f in direction for f in self.filter):
                continue

            dep_date, dep_time = dep.get("date"), dep.get("time")
            dep_dt = datetime.strptime(f"{dep_date} {dep_time}", "%Y-%m-%d %H:%M:%S")

            rt_date = dep.get("rtDate", dep_date)
            rt_time = dep.get("rtTime", dep_time)
            rt_dt = datetime.strptime(f"{rt_date} {rt_time}", "%Y-%m-%d %H:%M:%S")

            delay = int((rt_dt - dep_dt).total_seconds() // 60)
            delay_text = f"+{delay} min" if delay > 0 else ""

            short_dir = STATION_NAME_MAP.get(direction, direction)
            train_name = dep["name"].replace("Länstrafik - ", "")
            line_display = f"{train_name} → {short_dir}"

            countdown_base = rt_dt if delay > 0 else dep_dt

            result.append((line_display, dep_dt, rt_dt, countdown_base, delay_text))

        return sorted(result, key=lambda x: x[3])[:5]



