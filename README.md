# Noisemon

Noisemon è un progetto per l'analisi dei livelli di rumore basato su dati raccolti in un file CSV. Lo script Python `analysis.py` calcola i livelli di rumore equivalente (Leq) per le fasce orarie diurne e notturne per ciascun giorno presente nei dati.

## Struttura del Progetto

- `analysis.py`: Script principale che calcola i livelli di rumore equivalenti.
- `requirements.txt`: File delle dipendenze necessarie per eseguire lo script.

## Requisiti

- Python 3.6 o superiore

## Creazione di un Ambiente Virtuale

Per isolare le dipendenze del progetto, è consigliabile creare un ambiente virtuale. Segui questi passaggi:

1. **Crea l'ambiente virtuale**:
   
   ```bash
   python -m venv venv
   ```

   Questo comando creerà una cartella chiamata `venv` nella quale verrà installato Python e le dipendenze del progetto.

2. **Attiva l'ambiente virtuale**:

   - Su **Windows**:

     ```bash
     venv\Scripts\activate
     ```

   - Su **macOS/Linux**:

     ```bash
     source venv/bin/activate
     ```

   Dopo aver attivato l'ambiente virtuale, il prompt della tua shell dovrebbe cambiare per indicare che sei all'interno dell'ambiente virtuale.

3. **Installa le dipendenze**:

   Una volta attivato l'ambiente virtuale, installa le dipendenze specificate nel file `requirements.txt`:

   ```bash
   pip install -r requirements.txt
   ```

## Esecuzione dello Script

Per eseguire lo script, utilizza il seguente comando:

```bash
python analysis.py <path_to_csv_file>
```

Sostituisci `<path_to_csv_file>` con il percorso del tuo file CSV. Ad esempio:

```bash
python analysis.py data/noise_data.csv
```

## Esempio di File CSV

Il file CSV deve avere due colonne: `Timestamp` e `Measure`. Di seguito è riportato un esempio del formato del file:

```
Timestamp,Measure
2024-09-09 19:04:05,55.8
2024-09-09 19:04:06,56.0
2024-09-09 19:04:07,58.1
...
```

## Output

Lo script produrrà un output con i livelli di rumore equivalente diurno e notturno per ciascun giorno, nel formato:

```
Data        Leq_Diurno   Leq_Notturno
2024-09-09  56.75        48.32
2024-09-10  54.90        49.11
...
```

### Calcolo del Livello Equivalente di Rumore (Leq)

Lo script `analysis.py` calcola i livelli di rumore equivalente (Leq) per due fasce orarie: diurna e notturna. Ecco come viene effettuato il calcolo:

### Input

Il file CSV deve contenere due colonne:
- `Timestamp`: data e ora (in UTC).
- `Measure`: livello di rumore in dB.

### Conversione del Timestamp

I timestamp nel file CSV sono inizialmente in UTC. Vengono convertiti in ora italiana (CET/CEST) per il calcolo.

### Filtraggio dei Dati

I dati vengono suddivisi in due fasce orarie:
- **Fascia diurna**: dalle 06:00 alle 22:00 ora italiana.
- **Fascia notturna**: dalle 22:00 alle 06:00 del giorno successivo ora italiana.

### Calcolo del Leq

#### Leq diurno

Per la fascia diurna, il calcolo viene effettuato come segue:
- **Durata**: 16 ore (57600 secondi).
- **Formula**:
  
  `Leq_Day = 10 * log10((1 / 57600) * Σ(10^(Measure_i / 10)))`

  - **Spiegazione**: La formula calcola il livello equivalente di rumore durante il giorno come la media logaritmica ponderata dei valori di rumore. Qui, Σ rappresenta la somma dei valori di rumore convertiti dalla scala dei decibel a una scala lineare.

#### Leq notturno

Per la fascia notturna, il calcolo viene effettuato come segue:
- **Durata**: 8 ore (28800 secondi).
- **Formula**:
  
  `Leq_Night = 10 * log10((1 / 28800) * Σ(10^(Measure_i / 10)))`

  - **Spiegazione**: La formula calcola il livello equivalente di rumore durante la notte come la media logaritmica ponderata dei valori di rumore. Anche in questo caso, Σ rappresenta la somma dei valori di rumore convertiti dalla scala dei decibel a una scala lineare.

### Output

Lo script produce un output con i livelli di rumore equivalente diurno e notturno per ciascun giorno nel seguente formato:



### Output

Lo script produce un output con i livelli di rumore equivalente diurno e notturno per ciascun giorno nel seguente formato:

```
Data        Leq_Diurno   Leq_Notturno
2024-09-09  56.75        48.32
2024-09-10  54.90        49.11
...
```
```

## Contribuire

Se desideri contribuire a questo progetto, sentiti libero di fare fork del repository e di aprire una pull request.

## Licenza

Questo progetto è rilasciato sotto la licenza MIT.
