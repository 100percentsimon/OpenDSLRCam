# OpenDSLRCam - DSLR Webcam Steuerung

## Installation

1. Lade das Repository herunter:
    ```bash
    git clone https://github.com/100percentsimon/OpenDSLRCam.git
    cd OpenDSLRCam
    ```

2. Installiere die notwendigen Python-Abhängigkeiten:
    ```bash
    pip3 install -r requirements.txt
    ```

3. Stelle sicher, dass gphoto2 installiert ist:
    ```bash
    sudo apt install gphoto2
    ```

4. Kopiere die Konfigurationsdatei (config.cfg) an den richtigen Ort und passe sie an.

5. Aktiviere den Systemdienst:
    ```bash
    sudo cp opendslrcam.service /etc/systemd/system/
    sudo systemctl enable opendslrcam.service
    sudo systemctl start opendslrcam.service
    ```

6. Greife über deinen Webbrowser auf die Verwaltung zu:
    - `http://<RaspberryPi-IP>:5000`

---

## Benutzung

- Die Bilder werden automatisch alle 15 Minuten aufgenommen und hochgeladen.
- Die Web-Galerie wird automatisch auf der Webseite angezeigt und kann aufgerufen werden.

## Lizenz

OpenDSLRCam ist Open Source und unter der MIT Lizenz veröffentlicht.
