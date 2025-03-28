import os
import time
import subprocess
import configparser
import threading

# Standardwerte
DEFAULT_INTERVAL = 900  # 15 Minuten (900 Sekunden)
DEFAULT_FTP_HOST = "ftp://example.com"
DEFAULT_UPLOAD_SERVER = "/images"
DEFAULT_FTP_USERNAME = "user123"
DEFAULT_FTP_PASSWORD = "mypassword"
CONFIG_FILE = "/home/pi/OpenDSLRCam/config.cfg"
LOG_FILE = "/home/pi/OpenDSLRCam/logs/opendslrcam.log"
IMAGE_DIR = "/home/pi/OpenDSLRCam/images"
ARCHIVE_DIR = "/home/pi/OpenDSLRCam/archives"

# Sicherstellen, dass die Verzeichnisse existieren
os.makedirs(IMAGE_DIR, exist_ok=True)
os.makedirs(ARCHIVE_DIR, exist_ok=True)

# Konfiguration laden
def load_config():
    config = configparser.ConfigParser()
    config.read(CONFIG_FILE)
    
    interval = int(config.get('DEFAULT', 'Interval', fallback=DEFAULT_INTERVAL))
    ftp_host = config.get('DEFAULT', 'FTPHost', fallback=DEFAULT_FTP_HOST)
    upload_server = config.get('DEFAULT', 'UploadServer', fallback=DEFAULT_UPLOAD_SERVER)
    ftp_username = config.get('DEFAULT', 'FTPUsername', fallback=DEFAULT_FTP_USERNAME)
    ftp_password = config.get('DEFAULT', 'FTPPassword', fallback=DEFAULT_FTP_PASSWORD)
    
    return interval, ftp_host, upload_server, ftp_username, ftp_password

INTERVAL, FTP_HOST, UPLOAD_SERVER, FTP_USERNAME, FTP_PASSWORD = load_config()

# Funktion zur Aufnahme eines Bildes
def capture_image():
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    filename = f"{IMAGE_DIR}/{timestamp}.jpg"
    try:
        os.system(f"gphoto2 --capture-image-and-download --filename {filename}")
        log(f"Bild aufgenommen: {filename}")
        archive_image(filename)
        return filename
    except Exception as e:
        log(f"Fehler bei der Aufnahme: {str(e)}")
        return None

# Funktion zum Archivieren des Bildes
def archive_image(filepath):
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    archive_filepath = f"{ARCHIVE_DIR}/{timestamp}.jpg"
    try:
        os.rename(filepath, archive_filepath)
        log(f"Bild archiviert: {archive_filepath}")
    except Exception as e:
        log(f"Fehler beim Archivieren: {str(e)}")

# Automatische Aufnahme-Funktion
def auto_capture():
    global INTERVAL
    while True:
        capture_image()
        time.sleep(INTERVAL)

# Logging-Funktion
def log(message):
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a") as log_file:
        log_file.write(f"[{timestamp}] {message}\n")

# Überwachung und Statusabfrage
def show_status():
    with open(LOG_FILE, "r") as f:
        logs = f.readlines()[-10:]
    print("\n--- Letzte 10 Log-Einträge ---")
    for log_entry in logs:
        print(log_entry.strip())
    print("\n--- Aktuelle Einstellungen ---")
    print(f"Intervall: {INTERVAL} Sekunden")
    print(f"FTP Host: {FTP_HOST}")
    print(f"Upload Server: {UPLOAD_SERVER}")
    print(f"Benutzername: {FTP_USERNAME}")
    print("\n--- Ende der Statusausgabe ---")

# Startet die automatische Aufnahme und Statusüberwachung im Hintergrund
def start_program():
    threading.Thread(target=auto_capture, daemon=True).start()
    show_status()

if __name__ == '__main__':
    start_program()
    
    # Warte, bis der Benutzer das Programm stoppt
    while True:
        time.sleep(60)  # Alle 60 Sekunden die Log-Ausgabe anzeigen
        show_status()
