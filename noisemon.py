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


last_sync = datetime.now()

current_filename = None
current_file = None
current_writer = None

def store_measurement( measure=0.0):
    """Salva una misura nel file CSV."""
    global current_filename,current_file,current_writer
    ts=datetime.now();
    filename=f"{ts.strftime('%Y%m%d')}.csv"
    if current_filename!=filename:
        current_filename = filename
        current_file = open(filename, 'a')
        current_writer = csv.writer(current_file)
    current_writer.writerow([ts, measure])
        

async def notification_handler(sender, data):
    """Gestisce le notifiche dal dispositivo BLE."""
    global last_sync,current_file,current_filename
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
    
    store_measurement(dba_noise)
    
    if (datetime.now() - last_sync).total_seconds() >= 300:
        current_file.flush()
        await upload_to_google_drive(current_filename)
        print("File CSV sincronizzato con Google Drive.")
        last_sync = datetime.now()
    


async def upload_to_google_drive(file_name):
    """Carica o aggiorna il file CSV su Google Drive."""
    query = f"'{DRIVE_FOLDER_ID}' in parents and name='{file_name}'"
    results = service.files().list(q=query, fields="files(id)").execute()
    files = results.get('files', [])

    file_metadata = {
        'name': file_name,
        'parents': [DRIVE_FOLDER_ID]
    }
    media = MediaFileUpload(file_name, mimetype='text/csv')

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
    # Avvia i task di misurazione e sincronizzazione
    await asyncio.gather(
        measure_task(),
    )

if __name__ == "__main__":
    asyncio.run(main())
