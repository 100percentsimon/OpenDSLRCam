import os
import time
import subprocess
import threading
import psutil  # Zum Überwachen der Systemressourcen
from flask import Flask, render_template, request, redirect, url_for, jsonify

# Flask Web-GUI
app = Flask(__name__)

# Konfiguration
INTERVAL = 900  # 15 Minuten (900 Sekunden)
UPLOAD_SERVER = "ftp://yourserver.com/upload"
IMAGE_DIR = "/home/pi/OpenDSLRCam/images"
LOG_FILE = "/home/pi/OpenDSLRCam/logs/opendslrcam.log"
CONFIG_FILE = "/home/pi/OpenDSLRCam/config.cfg"
WEB_EXPORT_DIR = "/home/pi/OpenDSLRCam/web"

# Maximal erlaubte CPU- und RAM-Nutzung in Prozent
MAX_CPU_USAGE = 80
MAX_MEMORY_USAGE = 80

# Sicherstellen, dass die Verzeichnisse existieren
os.makedirs(IMAGE_DIR, exist_ok=True)
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
os.makedirs(WEB_EXPORT_DIR, exist_ok=True)

def load_config():
    if not os.path.exists(CONFIG_FILE):
        save_config(INTERVAL, UPLOAD_SERVER)
    with open(CONFIG_FILE, "r") as f:
        lines = f.readlines()
        return int(lines[0].strip()), lines[1].strip()

def save_config(interval, upload_server):
    with open(CONFIG_FILE, "w") as f:
        f.write(f"{interval}\n{upload_server}\n")

# Initiale Konfiguration laden
INTERVAL, UPLOAD_SERVER = load_config()

# Funktion zur Überprüfung der Systemressourcen
def check_system_resources():
    # CPU- und RAM-Auslastung überwachen
    cpu_usage = psutil.cpu_percent(interval=1)  # CPU-Auslastung in %
    memory_usage = psutil.virtual_memory().percent  # RAM-Auslastung in %

    log(f"CPU-Auslastung: {cpu_usage}% | RAM-Auslastung: {memory_usage}%")

    # Wenn CPU oder RAM die maximalen Schwellenwerte überschreiten, pausieren
    if cpu_usage > MAX_CPU_USAGE or memory_usage > MAX_MEMORY_USAGE:
        log("System überlastet, warte auf geringere Auslastung...")
        return False
    return True

# Funktion zur Aufnahme eines Bildes
def capture_image():
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    filename = f"{IMAGE_DIR}/{timestamp}.jpg"
    
    try:
        # Überprüfen, ob Systemressourcen verfügbar sind
        if not check_system_resources():
            log("Warte auf genügend Systemressourcen...")
            return None

        # Überprüfen und sicherstellen, dass keine anderen gphoto2-Prozesse laufen
        ensure_single_camera_access()

        # Bild aufnehmen und herunterladen
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
            # Überprüfen, ob Systemressourcen verfügbar sind
            if not check_system_resources():
                log("Warte auf genügend Systemressourcen für den Upload...")
                return

            # Bild hochladen
            os.system(f"curl -T {filepath} {UPLOAD_SERVER}")
            log(f"Bild hochgeladen: {filepath}")
        except Exception as e:
            log(f"Fehler beim Hochladen: {str(e)}")

# Automatische Aufnahme-Funktion mit Fehlerüberprüfung
def auto_capture():
    global INTERVAL
    while True:
        # Warte auf genügend Systemressourcen, bevor ein Bild aufgenommen wird
        if check_system_resources():
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
    global INTERVAL, UPLOAD_SERVER
    INTERVAL = int(request.form['interval'])
    UPLOAD_SERVER = request.form['upload_server']
    save_config(INTERVAL, UPLOAD_SERVER)
    return redirect(url_for('index'))

@app.route('/restart', methods=['POST'])
def restart():
    os.system("sudo systemctl restart opendslrcam.service")
    return "Service wird neu gestartet..."

# Starte Flask in eigenem Thread, damit das Hauptprogramm weiterläuft
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
