import gspread
import pandas as pd
import numpy as np
from google.colab import auth
from google.auth import default


class SheetConnector:
    """Classe per la gestione avanzata e flessibile di Google Sheets."""

    def __init__(self):
        auth.authenticate_user()
        creds, _ = default()
        self.client = gspread.authorize(creds)

    def get_smart_dataframe(
        self,
        sheet_url_or_id: str,
        header_keyword: str = "Frequenza",
        worksheet_identifier: str | int = 0,
    ) -> pd.DataFrame:
        """Cerca autonomamente la riga contenente la parola chiave (es. 'Frequenza'),

        la usa come intestazione della tabella e scarta i metadati superiori.
        """
        if sheet_url_or_id.startswith("http"):
            spreadsheet = self.client.open_by_url(sheet_url_or_id)
        else:
            spreadsheet = self.client.open_by_key(sheet_url_or_id)

        if isinstance(worksheet_identifier, int):
            worksheet = spreadsheet.get_worksheet(worksheet_identifier)
        else:
            worksheet = spreadsheet.worksheet(worksheet_identifier)

        # Scarica l'intera matrice grezza del foglio
        data = worksheet.get_all_values()

        # Trova la riga in cui compare la parola chiave (es. 'Frequenza')
        header_row_idx = None
        for idx, row in enumerate(data):
            if any(
                header_keyword.lower() in str(cell).lower() for cell in row
            ):
                header_row_idx = idx
                break

        if header_row_idx is None:
            raise ValueError(
                f"Impossibile trovare una riga con la parola chiave '{header_keyword}' nel foglio."
            )

        # Isola intestazioni e dati sottostanti
        headers = data[header_row_idx]
        rows = data[header_row_idx + 1 :]

        df = pd.DataFrame(rows, columns=headers)

        # Pulisce eventuali righe vuote
        df = df.dropna(how="all")
        df = df[df[headers[0]] != ""]  # Rimuove righe senza valore nella prima colonna

        return df