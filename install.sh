#!/bin/bash

# Update und Installation der benötigten Pakete
sudo apt update
sudo apt install -y python3-pip python3-gphoto2 curl git
sudo apt install -y python3-venv

# Erstelle und aktiviere ein virtuelles Python-Umfeld
python3 -m venv /home/pi/OpenDSLRCam/venv
source /home/pi/OpenDSLRCam/venv/bin/activate

# Installiere Python-Abhängigkeiten
pip install --upgrade pip
pip install gphoto2

# Klone das GitHub-Repository
git clone https://github.com/DeinGitHubRepo/OpenDSLRCam.git /home/pi/OpenDSLRCam

# Erstelle die Verzeichnisse, falls sie nicht existieren
mkdir -p /home/pi/OpenDSLRCam/images /home/pi/OpenDSLRCam/logs /home/pi/OpenDSLRCam/archives

# Konfigurationsdatei mit Standardwerten erstellen
echo "[DEFAULT]
Interval=900
FTPHost=ftp://example.com
UploadServer=/images
FTPUsername=user123
FTPPassword=mypassword" > /home/pi/OpenDSLRCam/config.cfg

# Erstelle den systemd-Service für den automatischen Start
echo "[Unit]
Description=OpenDSLRCam Service
After=network.target

[Service]
ExecStart=/home/pi/OpenDSLRCam/venv/bin/python3 /home/pi/OpenDSLRCam/app.py
WorkingDirectory=/home/pi/OpenDSLRCam
Restart=always
User=pi
Group=pi

[Install]
WantedBy=multi-user.target" > /etc/systemd/system/opendslrcam.service

# Aktiviere den Service
sudo systemctl enable opendslrcam.service
sudo systemctl start opendslrcam.service

echo "Installation abgeschlossen und der Dienst wurde gestartet."
