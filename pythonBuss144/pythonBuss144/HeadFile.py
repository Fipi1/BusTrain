import tkinter as tk
from tkinter import ttk
from datetime import datetime
from PIL import Image, ImageTk

from Bus.Bus import Buss144, Buss144Fruangen
from Train.Train import Train

# Initiera boards
buss = Buss144()
buss_fruangen = Buss144Fruangen()
tag = Train()

STOPS = [buss, buss_fruangen, tag]

departures_data = {s.name: [] for s in STOPS}
last_fetch = {s.name: None for s in STOPS}

tables = {}
frames = {}  # för att kunna dölja/visa sektioner

# ----------------------------
# GUI
# ----------------------------
root = tk.Tk()
root.title("Live-tavla: Buss + Tåg")

# Ladda logga och ikoner
logo_img = Image.open("sl.png").resize((100, 100))
logo_photo = ImageTk.PhotoImage(logo_img)

bus_img = Image.open("bus.png").resize((30, 30))
bus_icon = ImageTk.PhotoImage(bus_img)

train_img = Image.open("train.png").resize((30, 30))
train_icon = ImageTk.PhotoImage(train_img)

# SL logga
logo_label = tk.Label(root, image=logo_photo)
logo_label.pack(pady=10)

# Stor klocka
clock_label = tk.Label(root, text="", font=("Arial", 32, "bold"))
clock_label.pack(pady=10)


# ----------------------------
# Tabeller för varje stopp
# ----------------------------
for stop in STOPS:
    frame = tk.Frame(root)

    # Välj ikon baserat på namn
    if "Buss" in stop.name:
        icon = bus_icon
    elif "Pendeltåg" in stop.name:
        icon = train_icon
    else:
        icon = None

    # Rubrik med ikon
    header = tk.Frame(frame)
    if icon:
        icon_label = tk.Label(header, image=icon)
        icon_label.pack(side="left", padx=5)
    label = tk.Label(header, text=stop.name, font=("Arial", 14, "bold"))
    label.pack(side="left")
    header.pack(pady=(15, 5))

    # Starta med minimikolumner
    tree = ttk.Treeview(
        frame,
        columns=("Linje", "Planerad", "Nedräkning"),
        show="headings",
        height=5
    )
    tree.heading("Linje", text="Linje")
    tree.heading("Planerad", text="Planerad tid")
    tree.heading("Nedräkning", text="Tid kvar")
    tree.pack(expand=True, fill="both", padx=20)

    frame.pack(pady=(15, 5), fill="x")
    tables[stop.name] = tree
    frames[stop.name] = frame


# ----------------------------
# Uppdateringslogik
# ----------------------------
def update_board():
    now = datetime.now()
    clock_label.config(text=now.strftime("%H:%M:%S"))

    for stop in STOPS:
        # Dölj Fruängen före 16:00
        if "Fruängen" in stop.name and now.hour < 16:
            frames[stop.name].pack_forget()
            continue
        else:
            if "Fruängen" in stop.name and not frames[stop.name].winfo_ismapped():
                frames[stop.name].pack(pady=(15, 5), fill="x")

        # Hämta nytt var 30:e sekund
        if last_fetch[stop.name] is None or (now - last_fetch[stop.name]).total_seconds() > 30:
            departures_data[stop.name] = stop.fetch()
            last_fetch[stop.name] = now

        # Rensa tabellen
        tables[stop.name].delete(*tables[stop.name].get_children())

        # Kolla om någon avgång har försening
        has_delay = any(dep[4] for dep in departures_data[stop.name])

        # Sätt kolumner dynamiskt
        if has_delay:
            tables[stop.name]["columns"] = ("Linje", "Planerad", "Realtid", "Nedräkning", "Försening")
            for col in ("Linje", "Planerad", "Realtid", "Nedräkning", "Försening"):
                tables[stop.name].heading(col, text=col)
        else:
            tables[stop.name]["columns"] = ("Linje", "Planerad", "Nedräkning")
            for col in ("Linje", "Planerad", "Nedräkning"):
                tables[stop.name].heading(col, text=col)

        # Lägg till nya rader
        for line_name, dep_dt, rt_dt, countdown_base, delay_text in departures_data[stop.name]:
            countdown = countdown_base - now
            total_sec = int(countdown.total_seconds())
            if total_sec < 0:
                continue

            minutes = total_sec // 60
            seconds = total_sec % 60
            countdown_str = "Avgår nu" if (minutes == 0 and seconds == 0) else f"{minutes:02d}:{seconds:02d}"

            if delay_text:
                delay_text = f"⚠️ {delay_text}"

            # Färgkodning
            if minutes < 5:
                color = "green"
            elif minutes <= 15:
                color = "orange"
            else:
                color = "red"

            # Dynamiskt values beroende på försening
            if not delay_text:
                values = (line_name, dep_dt.strftime("%H:%M:%S"), countdown_str)
            else:
                values = (line_name, dep_dt.strftime("%H:%M:%S"),
                          rt_dt.strftime("%H:%M:%S"), countdown_str, delay_text)

            tables[stop.name].insert("", "end", values=values, tags=(color,))

        # Färginställningar
        tables[stop.name].tag_configure("green", foreground="green")
        tables[stop.name].tag_configure("orange", foreground="orange")
        tables[stop.name].tag_configure("red", foreground="red")

    root.after(1000, update_board)


update_board()
root.mainloop()
