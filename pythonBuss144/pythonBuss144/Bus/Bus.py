import requests
from datetime import datetime
import json

API_KEY = st.secrets["API_KEY"]
STATION_NAME_MAP = st.secrets["STATION_NAME_MAP"]


class Buss144:
    """Buss 144 mot Gullmarsplan från Myrvägen"""
    def __init__(self):
        self.name = "Buss 144 → Gullmarsplan (Myrvägen)"
        self.stop_id = "740065500"          # Myrvägen
        self.line_id = "1275014400001"      # Buss 144
        self.filter = "Gullmarsplan"

    def fetch(self):
        url = (
            f"https://api.resrobot.se/v2.1/departureBoard?"
            f"accessId={API_KEY}&id={self.stop_id}&lineId={self.line_id}&format=json&maxJourneys=10"
        )
        resp = requests.get(url)
        data = resp.json()

        result = []
        for dep in data.get("Departure", []):
            direction = dep["direction"]
            if self.filter not in direction:
                continue

            # Planerad tid
            dep_date, dep_time = dep.get("date"), dep.get("time")
            dep_dt = datetime.strptime(f"{dep_date} {dep_time}", "%Y-%m-%d %H:%M:%S")

            # Realtid
            rt_date = dep.get("rtDate", dep_date)
            rt_time = dep.get("rtTime", dep_time)
            rt_dt = datetime.strptime(f"{rt_date} {rt_time}", "%Y-%m-%d %H:%M:%S")

            # Försening
            delay = int((rt_dt - dep_dt).total_seconds() // 60)
            delay_text = f"+{delay} min" if delay > 0 else ""

            # Bussnamn
            bus_number = dep.get("line", dep.get("num", "")) or dep["name"].split()[-1]
            short_dir = STATION_NAME_MAP.get(direction, direction)
            line_display = f"Buss {bus_number} → {short_dir}"

            # Om det är försening → räkna ner mot rt_dt, annars dep_dt
            countdown_base = rt_dt if delay > 0 else dep_dt

            result.append((line_display, dep_dt, rt_dt, countdown_base, delay_text))

        return sorted(result, key=lambda x: x[3])[:5]


class Buss144Fruangen:
    """Buss 144 mot Fruängen från Älvsjö station"""
    def __init__(self):
        self.name = "Buss 144 → Fruängen (Älvsjö station)"
        self.stop_id = "740000789"          # Älvsjö station
        self.line_id = "1275014400001"      # Buss 144
        self.filter = "Fruängen"

    def fetch(self):
        url = (
            f"https://api.resrobot.se/v2.1/departureBoard?"
            f"accessId={API_KEY}&id={self.stop_id}&lineId={self.line_id}&format=json&maxJourneys=10"
        )
        resp = requests.get(url)
        data = resp.json()

        result = []
        for dep in data.get("Departure", []):
            direction = dep["direction"]
            if self.filter not in direction:
                continue

            dep_date, dep_time = dep.get("date"), dep.get("time")
            dep_dt = datetime.strptime(f"{dep_date} {dep_time}", "%Y-%m-%d %H:%M:%S")

            rt_date = dep.get("rtDate", dep_date)
            rt_time = dep.get("rtTime", dep_time)
            rt_dt = datetime.strptime(f"{rt_date} {rt_time}", "%Y-%m-%d %H:%M:%S")

            delay = int((rt_dt - dep_dt).total_seconds() // 60)
            delay_text = f"+{delay} min" if delay > 0 else ""

            bus_number = dep.get("line", dep.get("num", "")) or dep["name"].split()[-1]
            short_dir = STATION_NAME_MAP.get(direction, direction)
            line_display = f"Buss {bus_number} → {short_dir}"

            countdown_base = rt_dt if delay > 0 else dep_dt

            result.append((line_display, dep_dt, rt_dt, countdown_base, delay_text))

        return sorted(result, key=lambda x: x[3])[:5]


