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

## Contribuire

Se desideri contribuire a questo progetto, sentiti libero di fare fork del repository e di aprire una pull request.

## Licenza

Questo progetto è rilasciato sotto la licenza MIT.
