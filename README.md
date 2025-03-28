
# OpenDSLRCam

OpenDSLRCam ist ein Python-basiertes Tool, das eine Kamera über `gphoto2` steuert, regelmäßig Fotos aufnimmt und diese automatisch auf einen FTP-Server hochlädt. Es bietet auch eine einfache Möglichkeit, Systemprozesse zu überwachen und zu steuern, die mit der Kamera und dem FTP-Upload zusammenhängen.

## Features

- Aufnahme von Fotos mit einer Canon-Kamera oder einer kompatiblen Kamera.
- Automatisches Hochladen der Fotos auf einen FTP-Server.
- Anpassbare Intervalle für Fotoaufnahmen und das Beenden von gphoto2-Prozessen.
- Speicherung der Fotos lokal und im Archiv.
- Systemd-Dienst zur automatischen Ausführung im Hintergrund.

## Voraussetzungen

Bevor du das Projekt verwenden kannst, stelle sicher, dass du die folgenden Voraussetzungen erfüllst:

- Ein Raspberry Pi oder ein Linux-Server
- `gphoto2`-Tool zur Steuerung der Kamera
- Python 3.7+ und `pip` für Python-Paketmanagement

### Installiere Abhängigkeiten

Stelle sicher, dass `gphoto2` und Python 3 sowie die entsprechenden Abhängigkeiten installiert sind:

```bash
sudo apt-get update
sudo apt-get install gphoto2 python3 python3-pip python3-venv
```

## Installation

### 1. Repository klonen

Klonen Sie das GitHub-Repository auf dein System:

```bash
git clone https://github.com/USERNAME/OpenDSLRCam.git
cd OpenDSLRCam
```

### 2. Virtuelle Umgebung einrichten

Erstelle und aktiviere eine virtuelle Umgebung, um Abhängigkeiten zu installieren:

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Abhängigkeiten installieren

Installiere die benötigten Python-Pakete:

```bash
pip install -r requirements.txt
```

### 4. Konfigurationsdatei anpassen

Bearbeite die Konfigurationsdatei `config.cfg`, um die FTP-Server-Informationen und die gewünschten Intervallwerte zu setzen. Beispiel:

```ini
[FTP]
SERVER = ftp.example.com       # Dein FTP-Server
USER = username                # Dein FTP-Benutzername
PASSWORD = password            # Dein FTP-Passwort
REMOTE_PATH = /remote/path/    # Zielordner auf dem FTP-Server

[Settings]
PHOTO_INTERVAL = 600           # Interval in Sekunden zwischen Fotoaufnahmen (z.B. 600 für alle 10 Minuten)
KILL_INTERVAL = 3600           # Interval in Sekunden für den Kill-Befehl (z.B. 3600 für jede Stunde)
```

### 5. Systemd-Dienst einrichten

Damit das Programm automatisch im Hintergrund läuft, kannst du einen `systemd`-Dienst einrichten. Erstelle eine Datei für den Dienst:

```bash
sudo nano /etc/systemd/system/opendslrcam.service
```

Füge den folgenden Inhalt in die Datei ein:

```ini
[Unit]
Description=OpenDSLRCam Service
After=network.target

[Service]
ExecStart=/home/pi/OpenDSLRCam/venv/bin/python3 /home/pi/OpenDSLRCam/app.py
WorkingDirectory=/home/pi/OpenDSLRCam
Environment="PATH=/home/pi/OpenDSLRCam/venv/bin"
Restart=always
User=pi

[Install]
WantedBy=multi-user.target
```

Speichere die Datei und schließe den Editor.

### 6. Dienst aktivieren und starten

Aktiviere den Dienst, damit er bei jedem Systemstart automatisch ausgeführt wird:

```bash
sudo systemctl enable opendslrcam.service
sudo systemctl start opendslrcam.service
```

### 7. Überprüfen, ob der Dienst läuft

Du kannst den Status des Dienstes überprüfen, um sicherzustellen, dass er ordnungsgemäß läuft:

```bash
sudo systemctl status opendslrcam.service
```

## Nutzung

Sobald der Dienst gestartet wurde, wird das Programm alle 10 Minuten automatisch ein Foto aufnehmen und es auf den angegebenen FTP-Server hochladen. Der Dienst überprüft auch regelmäßig die Verbindung zur Kamera und startet den Dienst neu, falls ein Problem auftritt.

### Anpassung der Intervalle

- **PHOTO_INTERVAL**: Das Intervall für Fotoaufnahmen in Sekunden (z.B. `600` für 10 Minuten).
- **KILL_INTERVAL**: Das Intervall für das Beenden von gphoto2-Prozessen in Sekunden (z.B. `3600` für 1 Stunde).

### Fotoaufnahme und FTP-Upload

- Das Programm speichert das Foto zunächst lokal und benennt es in `LatestImage.jpg` um.
- Das Bild wird auf die Auflösung von `1920x1080` heruntergerechnet.
- Das Foto wird im lokalen Ordner `Images` und zusätzlich im `archives` Ordner für die Archivierung gespeichert.
- Danach wird das Bild auf den angegebenen FTP-Server hochgeladen.

## Logs

Die Logs des Programms werden in der Datei `opendslrcam.log` gespeichert. Du kannst die Logs mit folgendem Befehl einsehen:

```bash
tail -f /home/pi/OpenDSLRCam/opendslrcam.log
```

## Fehlerbehebung

- **Fehler beim FTP-Upload**: Überprüfe die FTP-Serveradresse, den Benutzernamen und das Passwort in der `config.cfg`.
- **Fehler bei der Kameraerkennung**: Stelle sicher, dass die Kamera ordnungsgemäß angeschlossen ist und von `gphoto2` unterstützt wird.
- **gphoto2-Prozesse beenden**: Wenn das Programm Probleme mit laufenden `gphoto2`-Prozessen hat, wird der Kill-Befehl automatisch ausgeführt. Falls dies nicht funktioniert, kannst du manuell den Befehl ausführen:

```bash
pkill -f gphoto2
```

## Lizenz

OpenDSLRCam ist unter der [MIT-Lizenz](LICENSE) lizenziert.
