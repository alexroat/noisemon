import pandas as pd
import numpy as np
import argparse

def calculate_leq(group):
    # Imposta gli orari di inizio e fine per la fascia diurna e notturna
    day_start = pd.to_datetime('06:00:00').time()
    day_end = pd.to_datetime('22:00:00').time()
    night_start1 = pd.to_datetime('22:00:00').time()
    night_end1 = pd.to_datetime('23:59:59').time()
    night_start2 = pd.to_datetime('00:00:00').time()
    night_end2 = pd.to_datetime('06:00:00').time()

    # Filtra i dati per fascia diurna
    day_samples = group[
        (group.index.time >= day_start) & 
        (group.index.time < day_end)
    ]
    
    # Filtra i dati per fascia notturna
    night_samples = group[
        ((group.index.time >= night_start1) & (group.index.time <= night_end1)) |
        ((group.index.time >= night_start2) & (group.index.time <= night_end2))
    ]

    # Calcolo Leq diurno
    if not day_samples.empty:
        num_samples_day = len(day_samples)
        leq_day = 10 * np.log10((1 / num_samples_day) * np.sum(10 ** (day_samples['Measure'] / 10)))
    else:
        leq_day = np.nan  # Se non ci sono dati

    # Calcolo Leq notturno
    if not night_samples.empty:
        num_samples_night = len(night_samples)
        leq_night = 10 * np.log10((1 / num_samples_night) * np.sum(10 ** (night_samples['Measure'] / 10)))
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
