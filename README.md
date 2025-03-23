OpenDSLRCam - Open Source DSLR Webcam System

✨ Was ist OpenDSLRCam?

OpenDSLRCam ist ein Open-Source-Tool für Raspberry Pi, das DSLR-Kameras als hochwertige Webcams oder Zeitraffer-Kameras nutzt. Das System ermöglicht automatisierte Aufnahmen, Cloud-Uploads, eine Web-Oberfläche zur Steuerung und ein automatisches Update-System.

💡 Funktionen

✔ Unterstützung für alle gphoto2-kompatiblen Kameras (Canon, Nikon, Sony, usw.)

✔ Web-GUI zur einfachen Steuerung & Konfiguration (ohne Terminal!)

✔ Einstellbares Aufnahmeintervall (z. B. alle 15 Minuten ein Foto)

✔ Upload auf Webserver (FTP, SFTP, WebDAV, Google Drive, Dropbox optional)

✔ Selbstüberwachung & Neustart bei Fehlern

✔ Automatische Updates mit nur einem Klick

✔ Installation als .deb-Paket für einfache Nutzung

⚙️ Installation

Voraussetzungen:

Raspberry Pi (Model B+ bis Raspberry Pi 5)

Python 3.x

gphoto2 installiert

1. OpenDSLRCam herunterladen & installieren

sudo apt update && sudo apt install -y python3 python3-pyqt5 python3-flask gphoto2 curl

# Repository klonen
git clone https://github.com/DEIN-GITHUB/OpenDSLRCam.git
cd OpenDSLRCam

# Skript ausführen
python3 src/opendslrcam.py

2. Web-Oberfläche starten

Nach dem Start ist die Web-GUI unter http://localhost:5000 erreichbar.

3. Optional: Installation als .deb-Paket

dpkg -i OpenDSLRCam.deb

🔧 Nutzung

Manuelles Foto aufnehmen

➡️ Web-GUI öffnen: http://localhost:5000

Button "Foto aufnehmen" klicken

Automatische Fotoaufnahmen

Standardintervall: alle 15 Minuten

Kann in der Web-GUI angepasst werden

Upload-Funktion

Konfigurierbar über config.json

Unterstützte Methoden: FTP, SFTP, WebDAV, Google Drive, Dropbox

🚀 Update & Wartung

Automatische Updates aktivieren

python3 src/opendslrcam.py --update

Logdateien anzeigen

tail -f logs/opendslrcam.log

💪 Mitmachen & Beitragen

OpenDSLRCam ist ein Open-Source-Projekt! Du kannst es weiterentwickeln und verbessern:

Forke das Repository auf GitHub

Erstelle neue Features oder behebe Bugs

Stelle einen Pull Request

Wir freuen uns über deine Ideen & Unterstützung!

GitHub: https://github.com/DEIN-GITHUB/OpenDSLRCam

🛠 Support

Falls du Probleme hast, kannst du uns gerne über die GitHub-Issues kontaktieren!

Erstellt von: Simon Grässle Lizenz: MIT License
