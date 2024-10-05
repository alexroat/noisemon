import asyncio
from bleak import BleakClient
import csv
import os
from datetime import datetime
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from dotenv import load_dotenv

# Carica le variabili d'ambiente dal file .env
load_dotenv()

# Ottieni le variabili d'ambiente dal file .env o utilizza i valori predefiniti
DEVICE_ADDRESS = os.getenv('DEVICE_ADDRESS', 'A13C58CF-5038-CD24-39AF-77FDB6273E3A')
WRITE_CHARACTERISTIC_UUID = os.getenv('WRITE_CHARACTERISTIC_UUID', '0000ff01-0000-1000-8000-00805f9b34fb')
NOTIFY_CHARACTERISTIC_UUID = os.getenv('NOTIFY_CHARACTERISTIC_UUID', '0000ff02-0000-1000-8000-00805f9b34fb')
CREDENTIALS_PATH = os.getenv('CREDENTIALS_PATH', 'credentials.json')
DRIVE_FOLDER_ID = os.getenv('DRIVE_FOLDER_ID', '1AiQ7WapJM2mfcJJuLeSGUR4daD5hQII_')
CSV_FILE_DIR = os.getenv('CSV_FILE_DIR', '/tmp')
CSV_FILE_NAME_PREFIX = os.getenv('CSV_FILE_NAME_PREFIX', 'misure')

# Configurazione delle credenziali e connessione a Google Drive
creds = Credentials.from_service_account_file(CREDENTIALS_PATH)
service = build('drive', 'v3', credentials=creds)

# Nome del file CSV locale
local_file_name = os.path.join(CSV_FILE_DIR, f"{datetime.now().strftime('%Y%m%d')}_{CSV_FILE_NAME_PREFIX}.csv")

# Inizializzazione del file CSV locale
def init_csv_file():
    """Inizializza il file CSV con l'intestazione, se vuoto."""
    if not os.path.exists(local_file_name) or os.path.getsize(local_file_name) == 0:
        with open(local_file_name, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['Timestamp', 'Measure'])

async def notification_handler(sender, data):
    """Gestisce le notifiche dal dispositivo BLE."""
    value = data.hex()
    condensed = value.replace(' ', '')
    bytemsg = bytes.fromhex(condensed)

    # Verifica e parsing dei dati
    assert bytemsg[4] == 0x3b  # Uni-T UT353BT noise meter
    assert bytemsg[14] == 0x3d  # dB(A) units

    value = bytemsg[5:].split(b'=')[0]
    assert b'dBA' in value
    raw_value = value.split(b'dBA')[0]

    dba_noise = float(raw_value.decode('ascii'))
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(timestamp, dba_noise)

    # Scrivi la misura direttamente sul file CSV
    with open(local_file_name, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([timestamp, dba_noise])

async def upload_to_google_drive():
    """Carica o aggiorna il file CSV su Google Drive."""
    file_name = os.path.basename(local_file_name)
    query = f"'{DRIVE_FOLDER_ID}' in parents and name='{file_name}'"
    results = service.files().list(q=query, fields="files(id)").execute()
    files = results.get('files', [])

    file_metadata = {
        'name': file_name,
        'parents': [DRIVE_FOLDER_ID]
    }
    media = MediaFileUpload(local_file_name, mimetype='text/csv')

    try:
        if files:
            file_id = files[0]['id']
            service.files().update(fileId=file_id, media_body=media).execute()
            print(f"File {file_name} aggiornato su Google Drive con ID {file_id}.")
        else:
            service.files().create(body=file_metadata, media_body=media, fields='id').execute()
            print(f"File {file_name} creato su Google Drive.")
    except Exception as e:
        print(f"Errore durante il salvataggio su Google Drive: {e}")

async def save_and_sync_file():
    """Task che salva e sincronizza periodicamente il file CSV su Google Drive."""
    while True:
        await asyncio.sleep(60)  # Aspetta 60 secondi tra le sincronizzazioni
        await upload_to_google_drive()

async def measure_task():
    """Task per connettersi al dispositivo BLE e gestire la raccolta delle misure."""
    while True:
        try:
            async with BleakClient(DEVICE_ADDRESS) as client:
                print("Connesso al dispositivo BLE")
                await client.start_notify(NOTIFY_CHARACTERISTIC_UUID, notification_handler)
                while True:
                    await client.write_gatt_char(WRITE_CHARACTERISTIC_UUID, b'\x5e')  # Richiedi una misura
                    await asyncio.sleep(1)  # Intervallo tra le richieste
        except Exception as e:
            print(f"Errore nella connessione al dispositivo: {e}. Riprovo in 5 secondi...")
            await asyncio.sleep(5)

async def main():
    """Funzione principale per avviare i task."""
    init_csv_file()  # Inizializza il file CSV prima di avviare i task
    # Avvia i task di misurazione e sincronizzazione
    await asyncio.gather(
        measure_task(),
        save_and_sync_file()
    )

if __name__ == "__main__":
    asyncio.run(main())
