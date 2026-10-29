import io
import re

import pandas as pd
import requests


def _col_to_idx(col) -> int:
    """Accetta una lettera ('A', 'ab') o un indice 0-based e restituisce l'indice 0-based."""
    if isinstance(col, int) and col >= 0:
        return col
    if isinstance(col, str) and re.fullmatch(r"[A-Za-z]+", col.strip()):
        idx = 0
        for ch in col.strip().upper():
            idx = idx * 26 + (ord(ch) - 64)
        return idx - 1
    raise ValueError(f"Colonna non valida: {col!r}")


class SheetConnector:
    """
    Legge tabelle da un Google Sheet condiviso come
    'Chiunque abbia il link > Visualizzatore'. Nessun login, nessun segreto.
    """

    def get_table_block(
        self,
        sheet_url: str,
        start_col,
        end_col,
        header_row_idx: int = 8,
        worksheet_identifier: str | int = 0,
        end_row: int = 100,
    ) -> pd.DataFrame:
        """
        Estrae una sotto-tabella (blocco verticale), utile con più tabelle affiancate.

        - sheet_url: URL del foglio (il #gid, se presente, viene ignorato).
        - start_col, end_col: colonne come lettera ('A', 'I') o indice 0-based.
        - header_row_idx: indice 0-based (da riga 1 del foglio) della riga delle intestazioni.
        - worksheet_identifier: nome della scheda ("Misure") oppure indice 0-based.
        - end_row: ultima riga letta.
        """
        m = re.search(r"/spreadsheets/d/([a-zA-Z0-9_-]+)", sheet_url)
        if not m:
            raise ValueError("URL non valido: deve contenere /spreadsheets/d/<ID>")

        # Si scarica il foglio come file Excel: contiene i nomi delle schede e numeri già numerici
        resp = requests.get(
            f"https://docs.google.com/spreadsheets/d/{m.group(1)}/export",
            params={"format": "xlsx"}, timeout=60,
        )
        if resp.status_code != 200 or not resp.content.startswith(b"PK"):  # xlsx = file zip
            raise PermissionError(
                "Foglio non accessibile. Imposta Condividi > 'Chiunque abbia il link' > Visualizzatore."
            )

        xl = pd.ExcelFile(io.BytesIO(resp.content))
        if isinstance(worksheet_identifier, str) and worksheet_identifier not in xl.sheet_names:
            raise KeyError(f"Scheda {worksheet_identifier!r} non trovata. Schede presenti: {xl.sheet_names}")

        # Lettura dal bordo A1, così gli indici di riga/colonna coincidono con quelli del foglio
        raw = xl.parse(worksheet_identifier, header=None)
        raw = raw.iloc[:end_row, _col_to_idx(start_col):_col_to_idx(end_col) + 1]

        if len(raw) <= header_row_idx:
            raise ValueError(f"header_row_idx={header_row_idx} fuori range ({len(raw)} righe lette).")

        df = pd.DataFrame(raw.iloc[header_row_idx + 1:].values, columns=raw.iloc[header_row_idx].values)
        df = df.dropna(how="all")
        df = df.loc[:, [not pd.isna(c) and str(c).strip() != "" for c in df.columns]]
        return df.infer_objects()  # ripristina i tipi numerici (float/int) colonna per colonna
