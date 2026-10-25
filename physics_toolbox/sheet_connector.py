import gspread
import pandas as pd
import numpy as np
from google.colab import userdata
import json

class SheetConnector:
    """Gestisce la connessione a Google Sheets e l'estrazione di tabelle multiple affiancate."""
    
    def __init__(self):
        secret_json = userdata.get('GCP_SERVICE_ACCOUNT_JSON')
        creds_dict = json.loads(secret_json)
        self.client = gspread.service_account_from_dict(creds_dict)

    def get_table_block(
        self,
        sheet_url_or_id: str,
        start_col: int,
        end_col: int,
        header_row_idx: int = 8,
        worksheet_identifier: str | int = 0
    ) -> pd.DataFrame:
        """
        Estrae una specifica sotto-tabella (blocco verticale) basata su un range 
        di colonne e una riga di intestazione, gestendo fogli con più tabelle affiancate.
        
        Parametri:
        - start_col (int): Indice numerico della prima colonna della tabella (0-based, es. 0 per A).
        - end_col (int): Indice numerico dell'ultima colonna della tabella.
        - header_row_idx (int): Indice della riga che contiene le intestazioni per questo blocco.
        - worksheet_identifier: Nome o indice della scheda.
        """
        if sheet_url_or_id.startswith("http"):
            spreadsheet = self.client.open_by_url(sheet_url_or_id)
        else:
            spreadsheet = self.client.open_by_key(sheet_url_or_id)
            
        if isinstance(worksheet_identifier, int):
            worksheet = spreadsheet.get_worksheet(worksheet_identifier)
        else:
            worksheet = spreadsheet.worksheet(worksheet_identifier)
            
        # Scarica l'intera matrice del foglio
        data = worksheet.get_all_values()
        df_full = pd.DataFrame(data)
        
        # Taglia verticalmente il DataFrame prendendo solo le colonne del blocco desiderato
        df_block = df_full.iloc[:, start_col:end_col + 1]
        
        # Isola le intestazioni e i dati sottostanti per questo specifico blocco
        headers = df_block.iloc[header_row_idx].values
        rows = df_block.iloc[header_row_idx + 1:]
        
        df = pd.DataFrame(rows.values, columns=headers)
        
        # Pulizia: rimuove righe completamente vuote e colonne senza nome
        df = df.dropna(how="all")
        df = df.loc[:, df.columns != ""]
        
        return df