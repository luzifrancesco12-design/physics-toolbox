# physics_toolbox

Strumenti per il laboratorio di Segnali e Sistemi.

- `SheetConnector`: legge tabelle da un Google Sheet condiviso come "Chiunque abbia il link > Visualizzatore" (nessun login, nessun segreto).
- `BasePlotter`, `BodePlotter`: grafici con barre d'errore e diagrammi di Bode.

## Installazione (Colab)

```python
!pip install -q git+https://github.com/<UTENTE>/physics_toolbox.git
```

Per aggiornare all'ultima versione: aggiungi `--upgrade --force-reinstall --no-deps`.
Per bloccare una versione precisa: `...physics_toolbox.git@v0.1.0`.

## Uso

```python
from physics_toolbox import SheetConnector, BodePlotter

conn = SheetConnector()
df = conn.get_table_block(URL, "A", "I", header_row_idx=8, worksheet_identifier="Misure")

f    = df["Frequenza (Hz)"].to_numpy()
vin  = df["V_in (V)"].to_numpy()
vout = df["V_out (V)"].to_numpy()

bode = BodePlotter()
bode.plot_bode(f, vout / vin, is_db=False, label_mag="Misure")
bode.show()
```

Se una colonna numerica risulta di tipo testo (`df.dtypes`), converti con
`pd.to_numeric(df["col"], errors="coerce")`.

## Struttura

```
physics_toolbox/
├── pyproject.toml
└── physics_toolbox/
    ├── __init__.py
    ├── base_plotter.py
    ├── bode_plotter.py
    └── sheet_connector.py
```
