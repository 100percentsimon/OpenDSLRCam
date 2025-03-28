import os
import time
import subprocess
import threading
import requests
from flask import Flask, render_template, request, redirect, url_for, jsonify
import configparser

# Flask Web-GUI
app = Flask(__name__)

# Konfigurationsdatei und Verzeichnisse
CONFIG_FILE = "/home/pi/OpenDSLRCam/config.cfg"
IMAGE_DIR = "/home/pi/OpenDSLRCam/images"
LOG_FILE = "/home/pi/OpenDSLRCam/logs/opendslrcam.log"
WEB_EXPORT_DIR = "/home/pi/OpenDSLRCam/web"
GITHUB_REPO_URL = "https://github.com/100percentsimon/OpenDSLRCam.git"
GIT_DIR = "/home/pi/OpenDSLRCam"  # Der Ordner, in den die Dateien heruntergeladen werden

# Sicherstellen, dass die Verzeichnisse existieren
os.makedirs(IMAGE_DIR, exist_ok=True)
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
os.makedirs(WEB_EXPORT_DIR, exist_ok=True)

# Lade Konfiguration aus config.cfg
def load_config():
    config = configparser.ConfigParser()
    config.read(CONFIG_FILE)

    interval = config.getint('DEFAULT', 'Interval', fallback=900)  # Default: 15 Minuten
    upload_server = config.get('DEFAULT', 'UploadServer', fallback="ftp://yourserver.com/upload")
    ftp_username = config.get('DEFAULT', 'FTPUsername', fallback="your_ftp_username")
    ftp_password = config.get('DEFAULT', 'FTPPassword', fallback="your_ftp_password")

    return interval, upload_server, ftp_username, ftp_password

INTERVAL, UPLOAD_SERVER, FTP_USERNAME, FTP_PASSWORD = load_config()

# Funktion, um das Programm zu aktualisieren
def update_program():
    log("Prüfe auf Updates...")
    try:
        # Wechsel zum Git-Verzeichnis und pull die neuesten Änderungen
        os.chdir(GIT_DIR)
        result = subprocess.run(["git", "pull"], capture_output=True, text=True)
        if "Already up to date" in result.stdout:
            log("Das Programm ist bereits auf dem neuesten Stand.")
        else:
            log(f"Das Programm wurde erfolgreich aktualisiert: {result.stdout}")
        # Bereinigen Sie die Konfigurationsdateien, um keine Daten zu überschreiben
        preserve_config_file()
    except Exception as e:
        log(f"Fehler beim Aktualisieren des Programms: {str(e)}")

def preserve_config_file():
    """
    Sichert die Konfigurationsdatei, bevor die Dateien von GitHub heruntergeladen werden.
    """
    if os.path.exists(CONFIG_FILE):
        os.rename(CONFIG_FILE, f"{CONFIG_FILE}.backup")
        log(f"Konfigurationsdatei gesichert als {CONFIG_FILE}.backup")

# Funktion zur Aufnahme eines Bildes
def capture_image():
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    filename = f"{IMAGE_DIR}/{timestamp}.jpg"
    try:
        os.system(f"gphoto2 --capture-image-and-download --filename {filename}")
        log(f"Bild aufgenommen: {filename}")
        generate_web_gallery()
        return filename
    except Exception as e:
        log(f"Fehler bei der Aufnahme: {str(e)}")
        return None

# Funktion zum Hochladen des Bildes
def upload_image(filepath):
    if filepath and os.path.exists(filepath):
        try:
            # FTP-Upload
            os.system(f"curl -T {filepath} --user {FTP_USERNAME}:{FTP_PASSWORD} {UPLOAD_SERVER}")
            log(f"Bild hochgeladen: {filepath}")
        except Exception as e:
            log(f"Fehler beim Hochladen: {str(e)}")

# Automatische Aufnahme-Funktion mit Fehlerüberprüfung
def auto_capture():
    global INTERVAL
    while True:
        image = capture_image()
        if image:
            upload_image(image)
        else:
            restart_gphoto2()
        time.sleep(INTERVAL)

# Neustart von gphoto2 bei Problemen
def restart_gphoto2():
    log("Neustart von gphoto2...")
    os.system("sudo killall -9 gphoto2")
    time.sleep(2)
    os.system("gphoto2 --auto-detect")

# Logging-Funktion
def log(message):
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a") as log_file:
        log_file.write(f"[{timestamp}] {message}\n")

# Generiere JavaScript für die Galerie
def generate_web_gallery():
    images = sorted(os.listdir(IMAGE_DIR), reverse=True)[:100]  # Zeige die letzten 100 Bilder
    image_list = [f"/images/{img}" for img in images]
    
    js_code = f'''
    <script>
        var images = {image_list};
        var currentIndex = 0;
        function showImage(index) {{
            document.getElementById("galleryImage").src = images[index];
        }}
        function nextImage() {{
            if (currentIndex < images.length - 1) currentIndex++;
            showImage(currentIndex);
        }}
        function prevImage() {{
            if (currentIndex > 0) currentIndex--;
            showImage(currentIndex);
        }}
        window.onload = function() {{
            showImage(0);
        }};
    </script>
    <button onclick="prevImage()">Zurück</button>
    <img id="galleryImage" src="" width="600">
    <button onclick="nextImage()">Weiter</button>
    '''
    
    with open(f"{WEB_EXPORT_DIR}/gallery.js", "w") as f:
        f.write(js_code)
    log("Web-Galerie JavaScript generiert.")

# Flask Web-GUI Routen
@app.route('/')
def index():
    with open(LOG_FILE, "r") as f:
        logs = f.readlines()[-10:]
    return render_template('index.html', interval=INTERVAL, upload_server=UPLOAD_SERVER, logs=logs)

@app.route('/capture', methods=['POST'])
def manual_capture():
    image = capture_image()
    if image:
        upload_image(image)
        return "Bild aufgenommen und hochgeladen!"
    return "Fehler bei der Aufnahme."

@app.route('/gallery')
def gallery():
    return redirect("/web/gallery.js")

@app.route('/settings', methods=['POST'])
def settings():
    global INTERVAL, UPLOAD_SERVER, FTP_USERNAME, FTP_PASSWORD
    INTERVAL = int(request.form['interval'])
    UPLOAD_SERVER = request.form['upload_server']
    FTP_USERNAME = request.form['ftp_username']
    FTP_PASSWORD = request.form['ftp_password']
    
    # Konfiguration speichern
    save_config(INTERVAL, UPLOAD_SERVER, FTP_USERNAME, FTP_PASSWORD)
    
    return redirect(url_for('index'))

def save_config(interval, upload_server, ftp_username, ftp_password):
    config = configparser.ConfigParser()
    config.read(CONFIG_FILE)
    config.set('DEFAULT', 'Interval', str(interval))
    config.set('DEFAULT', 'UploadServer', upload_server)
    config.set('DEFAULT', 'FTPUsername', ftp_username)
    config.set('DEFAULT', 'FTPPassword', ftp_password)
    
    with open(CONFIG_FILE, "w") as configfile:
        config.write(configfile)

@app.route('/restart', methods=['POST'])
def restart():
    os.system("sudo systemctl restart opendslrcam.service")
    return "Service wird neu gestartet..."

# Startet Flask in eigenem Thread, damit das Hauptprogramm weiterläuft
def start_flask():
    app.run(host='0.0.0.0', port=5000, debug=False)

# Starte Flask-Webserver in separatem Thread
flask_thread = threading.Thread(target=start_flask)
flask_thread.daemon = True
flask_thread.start()

# Starte automatische Bildaufnahme in separatem Thread
auto_capture_thread = threading.Thread(target=auto_capture)
auto_capture_thread.daemon = True
auto_capture_thread.start()

log("OpenDSLRCam gestartet und bereit.")
