import os
import time
import subprocess
import threading
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

# Funktion zur Überprüfung, ob gphoto2-Prozesse laufen, und zum Beenden
def ensure_single_camera_access():
    # Beende alle gphoto2 Prozesse, die im Hintergrund laufen könnten
    os.system("sudo killall -9 gphoto2")
    time.sleep(2)  # Warten, damit Prozesse richtig beendet werden können

    # Überprüfe, ob gphoto2 noch läuft
    process_check = os.popen("ps aux | grep gphoto2").read()
    if 'gphoto2' not in process_check:
        log("Keine gphoto2 Prozesse gefunden. Kamera wird nun erkannt.")
    else:
        log("Es laufen noch gphoto2 Prozesse. Diese wurden gestoppt und die Kamera wird jetzt neu erkannt.")
    
    # Starte gphoto2 neu
    os.system("gphoto2 --auto-detect")

# Funktion zur Aufnahme eines Bildes
def capture_image():
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    filename = f"{IMAGE_DIR}/{timestamp}.jpg"
    try:
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
            os.system(f"curl -T {filepath} {UPLOAD_SERVER}")
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
