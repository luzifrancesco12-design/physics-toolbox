import gspread
import gspread.utils
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
        worksheet_identifier: str | int = 0,
        end_row: int = 100
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
            
        # Converte le lettere in numeri se l'utente passa stringhe (es. 'A' -> 0)
        if isinstance(start_col, str):
            start_col_num = gspread.utils.a1_to_rowcol(f"{start_col}1")[1]
        if isinstance(end_col, str):
            end_col_num = gspread.utils.a1_to_rowcol(f"{end_col}1")[1]
            
        if isinstance(worksheet_identifier, int):
            worksheet = spreadsheet.get_worksheet(worksheet_identifier)
        else:
            worksheet = spreadsheet.worksheet(worksheet_identifier)
            
        # Costruisce il range in stile Excel (es. "A1:I100") nativo di gspread
        range_notation = f"{start_col}1:{end_col}{end_row}"
        data = worksheet.get(range_notation)
        
        df_block = pd.DataFrame(data)
        
        # Isola le intestazioni e i dati sottostanti per questo specifico blocco
        headers = df_block.iloc[header_row_idx].values
        rows = df_block.iloc[header_row_idx + 1:]
        
        df = pd.DataFrame(rows.values, columns=headers)
        
        # Pulizia: rimuove righe completamente vuote e colonne senza nome
        df = df.dropna(how="all")
        df = df.loc[:, df.columns != ""]
        
        return df