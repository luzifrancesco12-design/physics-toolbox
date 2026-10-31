# physics_toolbox

Strumenti per il laboratorio di Segnali e Sistemi.

[![Apri in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/drive/1Sft5GLx97lTYJdF_0ACkUDuTRRm3AjFz)

Apri il template con il pulsante, poi `File ▸ Salva una copia in Drive` e lavora sulla copia.

## Contenuto

- `SheetConnector`: legge tabelle da un Google Sheet condiviso come "Chiunque abbia il link > Visualizzatore" (nessun login).
- `BasePlotter`, `BodePlotter`: grafici con barre d'errore e diagrammi di Bode.
- `analysis`: `Tabelle`, `fit`, `media_pesata`, `propaga`, `x_da_y`, `grafico_fit`, `fmt`, `salva`, `scarica_figure`. Guida di ogni funzione con `help(nome_funzione)`.

## Installazione manuale (Colab)

```python
!pip install -q git+https://github.com/luzifrancesco12-design/physics-toolbox.git
```

Per aggiornare: aggiungi `--upgrade --force-reinstall --no-deps`.
Per bloccare una versione: `...physics-toolbox.git@v0.1.0`.

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
