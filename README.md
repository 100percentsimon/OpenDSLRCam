# OpenDSLRCam

OpenDSLRCam ist ein automatisiertes System, das eine DSLR-Kamera steuert, regelmäßig Fotos aufnimmt, diese verkleinert, lokal speichert und anschließend auf einen FTP-Server hochlädt. Es wird in Python ausgeführt und verwendet `gphoto2` zur Steuerung der Kamera.

## Funktionen
- **Kameraerkennung und Fotoaufnahme**: Das Skript prüft alle 10 Minuten, ob eine Kamera angeschlossen ist, und nimmt dann ein Foto auf.
- **Bildbearbeitung**: Das aufgenommene Bild wird auf 1920x1080px verkleinert.
- **FTP-Upload**: Das Bild wird anschließend auf einen FTP-Server hochgeladen.
- **Archivierung**: Das Bild wird lokal gespeichert und archiviert.

## Voraussetzungen
- Raspberry Pi (oder ein anderes Linux-basiertes System)
- Eine DSLR-Kamera, die mit `gphoto2` kompatibel ist
- Python 3
- Die `gphoto2`-Software muss auf dem System installiert sein
- Die Python-Pakete `ftplib` und `Pillow` müssen installiert sein

## Installation

1. **Systemvoraussetzungen**:
   - Installiere `gphoto2`:
     ```bash
     sudo apt-get update
     sudo apt-get install gphoto2
     ```

2. **Python-Abhängigkeiten installieren**:
   - Erstelle und aktiviere eine virtuelle Umgebung:
     ```bash
     python3 -m venv venv
     source venv/bin/activate
     ```
   - Installiere die Abhängigkeiten:
     ```bash
     pip install -r requirements.txt
     ```

3. **Konfiguration**:
   - Kopiere die `config.cfg`-Datei und passe die Werte für FTP-Server, Benutzername und Passwort an.
   - Passe die Speicherpfade in der `config.cfg` an, wenn nötig.

4. **Systemd Service (optional)**:
   - Kopiere die Datei `opendslrcam.service` nach `/etc/systemd/system/`:
     ```bash
     sudo cp opendslrcam.service /etc/systemd/system/
     sudo systemctl daemon-reload
     sudo systemctl enable opendslrcam.service
     sudo systemctl start opendslrcam.service
     ```

5. **Starten des Programms**:
   - Du kannst das Programm auch manuell starten:
     ```bash
     python app.py
     ```

## Dateien

### `app.py`

Dies ist das Hauptskript, das alle Funktionen des Programms ausführt: Fotoaufnahme, Bildbearbeitung und FTP-Upload.

### `config.cfg`

Die Konfigurationsdatei, in der du FTP-Server, Pfade und Intervalle einstellen kannst.

### `opendslrcam.service`

Dies ist eine systemd-Service-Datei, mit der du das Skript als Dienst auf deinem Raspberry Pi ausführen kannst.

### `requirements.txt`

Diese Datei listet alle Python-Abhängigkeiten auf:
