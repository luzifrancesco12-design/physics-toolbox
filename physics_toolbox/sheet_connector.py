import gspread
import pandas as pd
import numpy as np
from google.colab import auth
from google.auth import default


class SheetConnector:
    """Classe per la gestione della connessione a Google Sheets e l'estrazione dati."""

    def __init__(self):
        """Esegue l'autenticazione interattiva dell'utente su Google Colab."""
        auth.authenticate_user()
        creds, _ = default()
        self.client = gspread.authorize(creds)

    def get_dataframe(
        self, sheet_url_or_id: str, worksheet_identifier: str | int = 0
    ) -> pd.DataFrame:
        """Apre un Google Sheet e carica l'intero foglio (o una scheda) in un DataFrame Pandas.

        Parametri:
        - sheet_url_or_id (str): URL completo oppure ID del Google Sheet.
        - worksheet_identifier (str | int): Nome della scheda (str) o indice (int, default=0).
        """
        if sheet_url_or_id.startswith("http"):
            spreadsheet = self.client.open_by_url(sheet_url_or_id)
        else:
            spreadsheet = self.client.open_by_key(sheet_url_or_id)

        if isinstance(worksheet_identifier, int):
            worksheet = spreadsheet.get_worksheet(worksheet_identifier)
        else:
            worksheet = spreadsheet.worksheet(worksheet_identifier)

        data = worksheet.get_all_records()
        return pd.DataFrame(data)

    def get_arrays(
        self,
        sheet_url_or_id: str,
        columns: list[str],
        worksheet_identifier: str | int = 0,
    ) -> list[np.ndarray]:
        """Estrae direttamente colonne specifiche dal foglio e le restituisce come un elenco di array NumPy.

        Parametri:
        - sheet_url_or_id (str): URL o ID del foglio Google.
        - columns (list): Elenco dei nomi delle colonne da estrarre (es. ['Frequenza', 'Guadagno']).
        - worksheet_identifier (str | int): Nome o indice del foglio.

        Ritorna:
        - Una lista di array NumPy corrispondenti alle colonne richieste.
        """
        df = self.get_dataframe(sheet_url_or_id, worksheet_identifier)

        arrays = []
        for col in columns:
            if col not in df.columns:
                raise KeyError(
                    f"La colonna '{col}' non è presente nel foglio Google."
                )
            arrays.append(df[col].to_numpy())

        return arrays