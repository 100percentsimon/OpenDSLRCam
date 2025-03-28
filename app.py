import os
import time
import subprocess
import logging
from datetime import datetime
from ftplib import FTP
from PIL import Image
import configparser

# Konfiguration aus der config.cfg Datei laden
config = configparser.ConfigParser()
config.read('/home/pi/OpenDSLRCam/config.cfg')

# FTP-Server-Konfiguration
FTP_SERVER = config.get('FTP', 'FTP_SERVER')
FTP_USER = config.get('FTP', 'FTP_USER')
FTP_PASSWORD = config.get('FTP', 'FTP_PASSWORD')

# Ordnerpfade
LOCAL_SAVE_PATH = config.get('Paths', 'LOCAL_SAVE_PATH')
IMAGES_FOLDER = config.get('Paths', 'IMAGES_FOLDER')
ARCHIVES_FOLDER = config.get('Paths', 'ARCHIVES_FOLDER')
REMOTE_PATH = config.get('Paths', 'REMOTE_PATH')

# Intervalle
PHOTO_INTERVAL = int(config.get('Settings', 'PHOTO_INTERVAL'))  # Interval für Fotos (in Sekunden)
KILL_INTERVAL = int(config.get('Settings', 'KILL_INTERVAL'))  # Interval für kill Befehl (in Sekunden)

# Logging-Konfiguration
LOG_FILE = "/home/pi/OpenDSLRCam/opendslrcam.log"
logging.basicConfig(filename=LOG_FILE, level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Sicherstellen, dass die Ordner existieren
os.makedirs(IMAGES_FOLDER, exist_ok=True)
os.makedirs(ARCHIVES_FOLDER, exist_ok=True)

def stop_gphoto2_process():
    """Beende alle gphoto2-Prozesse, falls sie aktiv sind."""
    try:
        logging.info("Überprüfe auf störende gphoto2-Prozesse...")
        subprocess.run(['pkill', '-f', 'gphoto2'], check=True)
        logging.info("gphoto2-Prozesse erfolgreich beendet.")
    except subprocess.CalledProcessError:
        logging.warning("Kein laufender gphoto2-Prozess gefunden.")
    except Exception as e:
        logging.error(f"Fehler beim Beenden von gphoto2: {e}")

def check_camera_connected():
    """Überprüft, ob die Kamera angeschlossen ist und angesprochen werden kann."""
    try:
        result = subprocess.run(['gphoto2', '--auto-detect'], capture_output=True, text=True)
        if "Canon" in result.stdout:  # Beispiel: Kamera ist von Canon
            logging.info("Kamera erkannt und bereit.")
            return True
        else:
            logging.warning("Keine Kamera erkannt.")
            return False
    except subprocess.CalledProcessError as e:
        logging.error(f"Fehler bei Kameraerkennung: {e}")
        return False
    except Exception as e:
        logging.error(f"Unbekannter Fehler: {e}")
        return False

def take_photo():
    """Macht ein Foto, speichert es lokal und verkleinert es."""
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = "LatestImage.jpg"
        original_filepath = os.path.join(LOCAL_SAVE_PATH, filename)

        # Foto aufnehmen und speichern
        logging.info(f"Starte Fotoaufnahme: {filename}")
        subprocess.run(['gphoto2', '--capture-image-and-download', '--filename', original_filepath], check=True)
        logging.info(f"Foto gespeichert: {original_filepath}")

        # Foto im 'archives' Ordner speichern
        archive_filepath = os.path.join(ARCHIVES_FOLDER, f"photo_{timestamp}.jpg")
        os.rename(original_filepath, archive_filepath)
        logging.info(f"Originalfoto im Archiv gespeichert: {archive_filepath}")

        # Foto auf 1920x1080 verkleinern und im 'Images' Ordner speichern
        image = Image.open(archive_filepath)
        image = image.resize((1920, 1080))
        image.save(os.path.join(IMAGES_FOLDER, filename))
        logging.info(f"Verkleinertes Bild gespeichert: {os.path.join(IMAGES_FOLDER, filename)}")

        return filename
    except subprocess.CalledProcessError as e:
        logging.error(f"Fehler bei Fotoaufnahme: {e}")
        return None
    except Exception as e:
        logging.error(f"Unbekannter Fehler bei Fotoaufnahme: {e}")
        return None

def upload_to_ftp(filename):
    """Lädt das aufgenommene Foto auf einen FTP-Server hoch."""
    try:
        ftp = FTP(FTP_SERVER)
        ftp.login(FTP_USER, FTP_PASSWORD)

        local_filepath = os.path.join(IMAGES_FOLDER, filename)
        remote_filepath = REMOTE_PATH + filename

        with open(local_filepath, "rb") as file:
            ftp.storbinary(f"STOR {remote_filepath}", file)

        ftp.quit()
        logging.info(f"Foto erfolgreich hochgeladen: {remote_filepath}")
    except Exception as e:
        logging.error(f"Fehler beim FTP-Upload: {e}")
def main():
    """Hauptprogramm-Loop"""
    camera_connected = False

    while True:
        # Überprüfe, ob die Kamera verbunden ist
        if check_camera_connected():
            # Wenn die Kamera erkannt wird, aber noch nicht verbunden war, setze die Variable
            if not camera_connected:
                camera_connected = True
                logging.info("Kamera erkannt. Starte Fotoaufnahme.")
            
            # Foto aufnehmen
            filename = take_photo()
            if filename:
                # Foto erfolgreich aufgenommen, jetzt hochladen
                upload_to_ftp(filename)
        
        # Wenn Kamera nicht mehr verbunden, führe Bereinigung durch
        elif camera_connected:
            camera_connected = False
            logging.warning("Kamera wurde getrennt! Beende gphoto2-Prozesse.")
            stop_gphoto2_process()

        # Alle X Sekunden ein neues Foto aufnehmen, unabhängig von der Kameraverbindung
        logging.info(f"Warte {PHOTO_INTERVAL} Sekunden, bevor das nächste Foto aufgenommen wird.")
        time.sleep(PHOTO_INTERVAL)  # Warten für PHOTO_INTERVAL Sekunden, bevor das nächste Foto aufgenommen wird


if __name__ == "__main__":
    main()
