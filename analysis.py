import pandas as pd
import numpy as np
import pytz
import argparse

def calculate_leq(group):
    # Fascia diurna: dalle 06:00 alle 22:00 ora italiana
    day_samples = group.between_time('06:00', '22:00')
    # Fascia notturna: dalle 22:00 alle 06:00 del giorno successivo
    night_samples = group.between_time('22:00', '06:00')

    # Calcolo Leq diurno (16 ore, quindi 57600 secondi)
    if not day_samples.empty:
        leq_day = 10 * np.log10((1 / 57600) * np.sum(10 ** (day_samples['Measure'] / 10)))
    else:
        leq_day = np.nan  # Se non ci sono dati

    # Calcolo Leq notturno (8 ore, quindi 28800 secondi)
    if not night_samples.empty:
        leq_night = 10 * np.log10((1 / 28800) * np.sum(10 ** (night_samples['Measure'] / 10)))
    else:
        leq_night = np.nan  # Se non ci sono dati

    return pd.Series({'Leq_Day': leq_day, 'Leq_Night': leq_night})

def main():
    # Definizione dei parametri di input con argparse
    parser = argparse.ArgumentParser(description='Calcola il Leq diurno e notturno da un file CSV contenente timestamp e valori dB.')
    parser.add_argument('csv_file', type=str, help='Percorso al file CSV')
    args = parser.parse_args()

    # Carica il file CSV
    try:
        # Prova a leggere il file con le intestazioni corrette
        df = pd.read_csv(args.csv_file)

        # Verifica se le colonne esistono
        if 'Timestamp' not in df.columns or 'Measure' not in df.columns:
            raise KeyError("Il file CSV non ha le colonne richieste 'Timestamp' e 'Measure'.")
        
    except FileNotFoundError:
        print(f"File non trovato: {args.csv_file}")
        return
    except pd.errors.EmptyDataError:
        print("Il file CSV è vuoto.")
        return
    except KeyError as e:
        print(e)
        return

    # Converti la colonna del timestamp in un formato datetime
    df['Timestamp'] = pd.to_datetime(df['Timestamp'], utc=True)

    # Imposta il fuso orario a UTC, poi convertilo a CET/CEST (ora italiana)
    df['Timestamp'] = df['Timestamp'].dt.tz_convert('Europe/Rome')

    # Raggruppa i dati per giorno e applica la funzione di calcolo del Leq
    result = df.set_index('Timestamp').groupby(pd.Grouper(freq='D')).apply(calculate_leq)

    # Stampa i risultati
    print("Data\t\tLeq_Diurno\tLeq_Notturno")
    for index, row in result.iterrows():
        leq_day = f"{row['Leq_Day']:.2f}" if not np.isnan(row['Leq_Day']) else "N/A"
        leq_night = f"{row['Leq_Night']:.2f}" if not np.isnan(row['Leq_Night']) else "N/A"
        print(f"{index.date()}\t{leq_day}\t\t{leq_night}")

if __name__ == "__main__":
    main()
