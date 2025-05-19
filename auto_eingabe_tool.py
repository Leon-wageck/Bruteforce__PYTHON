import tkinter as tk
from tkinter import filedialog, messagebox
import pyautogui
import keyboard
import threading
import time
import random
import string
import datetime
import os
import sys

# Arbeitsverzeichnis auf Skript- oder EXE-Ordner setzen
if getattr(sys, 'frozen', False):
    base_path = os.path.dirname(sys.executable)
else:
    base_path = os.path.dirname(os.path.abspath(__file__))

# Logs-Ordner erstellen
log_dir = os.path.join(base_path, "logs")
os.makedirs(log_dir, exist_ok=True)

# Log-Datei mit Zeitstempel
timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
logfile = os.path.join(log_dir, f"auto_eingabe_log_{timestamp}.txt")

# Einstellungen
eingabe_delay = 0.3
start_delay = 2
zufall_anzahl = 10
min_len = 5
max_len = 10
woerter_liste = []
stop_wort = ""
ziel_position = None
session_blacklist = set()

def schreibe_log(eingabe, status="OK"):
    try:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(logfile, "a", encoding="utf-8") as f:
            f.write(f"[{timestamp}] {eingabe} -> {status}\n")
    except Exception as e:
        print(f"\u26a0 Log konnte nicht geschrieben werden: {e}")

def zufaellige_kombination_einzigartig(min_len, max_len, blacklist):
    versuche = 0
    zeichen = ''
    if use_uppercase.get():
        zeichen += string.ascii_uppercase
    if use_lowercase.get():
        zeichen += string.ascii_lowercase
    if use_digits.get():
        zeichen += string.digits
    if use_specials.get():
        zeichen += string.punctuation
    if not zeichen:
        raise Exception("Keine Zeichentypen ausgewählt!")

    while versuche < 1000:
        laenge = random.randint(min_len, max_len)
        kombi = ''.join(random.choice(zeichen) for _ in range(laenge))
        if kombi not in blacklist:
            blacklist.add(kombi)
            return kombi
        versuche += 1
    raise Exception("Keine neuen Kombinationen mehr verfügbar.")

def lade_woerter(pfad):
    try:
        with open(pfad, "r", encoding="utf-8") as f:
            return [zeile.strip() for zeile in f if zeile.strip()]
    except Exception as e:
        messagebox.showerror("Fehler beim Laden", str(e))
        return []

def warte_auf_mausklick():
    info_label.config(text="➡ Klicke jetzt in das Eingabefeld (5 Sek. Zeit)...")
    time.sleep(5)
    global ziel_position
    ziel_position = pyautogui.position()
    info_label.config(text=f"📍 Zielposition gespeichert: {ziel_position}")

def warte_auf_enter():
    info_label.config(text="⏳ Warte auf ENTER zum Starten...")
    keyboard.wait("enter")
    info_label.config(text=f"▶️ Starte Eingabe in {start_delay} Sek...")
    time.sleep(start_delay)
    eingabe_starten()

def eingabe_starten():
    global ziel_position
    pyautogui.click(ziel_position)

    for wort in woerter_liste:
        pyautogui.write(wort)
        pyautogui.press("enter")
        schreibe_log(wort, status="OK")
        if stop_wort and wort == stop_wort:
            messagebox.showinfo("Stop-Wort erreicht", "Eingabe beendet.")
            return
        time.sleep(eingabe_delay)
        if keyboard.is_pressed("esc"):
            messagebox.showinfo("Abbruch", "Eingabe wurde per ESC gestoppt.")
            return

    for _ in range(zufall_anzahl):
        try:
            wort = zufaellige_kombination_einzigartig(min_len, max_len, session_blacklist)
            pyautogui.write(wort)
            pyautogui.press("enter")
            schreibe_log(wort, status="OK")
            if stop_wort and wort == stop_wort:
                messagebox.showinfo("Stop-Wort erreicht", "Eingabe beendet.")
                return
            time.sleep(eingabe_delay)
            if keyboard.is_pressed("esc"):
                messagebox.showinfo("Abbruch", "Eingabe wurde per ESC gestoppt.")
                return
        except Exception as e:
            messagebox.showerror("Fehler", f"Keine neuen Kombinationen verfügbar:\n{e}")
            return

    messagebox.showinfo("Fertig", "Eingabe abgeschlossen.")

def eingabe_vorbereiten():
    try:
        global min_len, max_len, zufall_anzahl, eingabe_delay, start_delay, stop_wort, session_blacklist
        session_blacklist = set()  # bei jedem neuen Start leeren
        min_len = int(entry_min_len.get())
        max_len = int(entry_max_len.get())
        zufall_anzahl = int(entry_zufall.get())
        eingabe_delay = float(entry_delay.get())
        start_delay = float(entry_start_delay.get())
        stop_wort = entry_stopwort.get()

        threading.Thread(target=warte_auf_mausklick, daemon=True).start()
        threading.Thread(target=warte_auf_enter, daemon=True).start()
    except ValueError:
        messagebox.showerror("Fehler", "Bitte gültige Werte eingeben.")

def datei_auswaehlen():
    pfad = filedialog.askopenfilename(filetypes=[("Textdateien", "*.txt")])
    if pfad:
        global woerter_liste
        woerter_liste = lade_woerter(pfad)
        label_datei.config(text=f"{len(woerter_liste)} Wörter geladen")

# GUI
root = tk.Tk()
root.title("Auto Login Eingabe Tool")

tk.Label(root, text="Startverzögerung (s):").grid(row=0, column=0)
entry_start_delay = tk.Entry(root)
entry_start_delay.insert(0, "2")
entry_start_delay.grid(row=0, column=1)

tk.Label(root, text="Eingabe-Verzögerung (s):").grid(row=1, column=0)
entry_delay = tk.Entry(root)
entry_delay.insert(0, "0.3")
entry_delay.grid(row=1, column=1)

tk.Label(root, text="Zufallsanzahl:").grid(row=2, column=0)
entry_zufall = tk.Entry(root)
entry_zufall.insert(0, "10")
entry_zufall.grid(row=2, column=1)

tk.Label(root, text="Minimale Zeichenlänge:").grid(row=3, column=0)
entry_min_len = tk.Entry(root)
entry_min_len.insert(0, "5")
entry_min_len.grid(row=3, column=1)

tk.Label(root, text="Maximale Zeichenlänge:").grid(row=4, column=0)
entry_max_len = tk.Entry(root)
entry_max_len.insert(0, "10")
entry_max_len.grid(row=4, column=1)

tk.Label(root, text="Stop-Wort:").grid(row=5, column=0)
entry_stopwort = tk.Entry(root)
entry_stopwort.grid(row=5, column=1)

label_datei = tk.Label(root, text="Keine Wörterdatei geladen")
label_datei.grid(row=6, column=0, columnspan=2)

tk.Button(root, text="Wörterdatei laden", command=datei_auswaehlen).grid(row=7, column=0, columnspan=2, pady=5)
tk.Button(root, text="Eingabe vorbereiten (Mausklick + ENTER)", command=eingabe_vorbereiten, bg="green", fg="white").grid(row=8, column=0, columnspan=2, pady=10)

# Optionen für Zeichentypen
use_uppercase = tk.BooleanVar(value=True)
use_lowercase = tk.BooleanVar(value=True)
use_digits = tk.BooleanVar(value=True)
use_specials = tk.BooleanVar(value=True)

tk.Checkbutton(root, text="Großbuchstaben (A-Z)", variable=use_uppercase).grid(row=10, column=0, sticky="w")
tk.Checkbutton(root, text="Kleinbuchstaben (a-z)", variable=use_lowercase).grid(row=10, column=1, sticky="w")
tk.Checkbutton(root, text="Zahlen (0-9)", variable=use_digits).grid(row=11, column=0, sticky="w")
tk.Checkbutton(root, text="Sonderzeichen (!@#)", variable=use_specials).grid(row=11, column=1, sticky="w")

info_label = tk.Label(root, text="⬆ Lade zuerst eine Wörterdatei und klicke dann 'Eingabe vorbereiten'. ESC = Abbruch")
info_label.grid(row=12, column=0, columnspan=2)

root.mainloop()
