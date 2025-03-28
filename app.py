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

# Funktion zum Deaktivieren von gvfs-gphoto2
def disable_gvfs_gphoto2():
    try:
        os.system("sudo systemctl stop gvfs-gphoto2-volume-monitor")
        os.system("sudo systemctl disable gvfs-gphoto2-volume-monitor")
        log("gvfs-gphoto2 Dienst gestoppt und deaktiviert.")
    except Exception as e:
        log(f"Fehler beim Deaktivieren von gvfs-gphoto2: {str(e)}")

# Funktion zum Erstellen der udev-Regel
def create_udev_rule():
    try:
        rule = 'ATTRS{idVendor}=="04a9", ATTRS{idProduct}=="32b4", ENV{UDISKS_IGNORE}="1"\n'
        with open("/etc/udev/rules.d/99-camera.rules", "w") as f:
            f.write(rule)
        os.system("sudo udevadm control --reload-rules")
        log("udev-Regel zur Verhinderung des automatischen Mountens der Kamera erstellt.")
    except Exception as e:
        log(f"Fehler beim Erstellen der udev-Regel: {str(e)}")

# Funktion zum Starten des Programms
def start_program():
    # Deaktivieren des gvfs-gphoto2-Dienstes
    disable_gvfs_gphoto2()

    # Erstellen der udev-Regel
    create_udev_rule()

    # Weiter mit der Initialisierung der Anwendung
    log("OpenDSLRCam startet...")
    # Weitere Programmlogik hier, z.B. Start der Flask-App, Bildaufnahme usw.

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

# Starte Flask-Webserver in separatem Thread
def start_flask():
    app.run(host='0.0.0.0', port=5000, debug=False)

# Starte automatische Bildaufnahme in separatem Thread
def auto_capture():
    global INTERVAL
    while True:
        image = capture_image()
        if image:
            upload_image(image)
        else:
            restart_gphoto2()
        time.sleep(INTERVAL)

# Starte das Programm
start_program()

# Starte Flask-Webserver und automatische Bildaufnahme
flask_thread = threading.Thread(target=start_flask)
flask_thread.daemon = True
flask_thread.start()

auto_capture_thread = threading.Thread(target=auto_capture)
auto_capture_thread.daemon = True
auto_capture_thread.start()

log("OpenDSLRCam gestartet und bereit.")
