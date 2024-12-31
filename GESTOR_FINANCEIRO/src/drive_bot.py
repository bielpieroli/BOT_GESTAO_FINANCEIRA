from dotenv import load_dotenv
import gspread
import json
import os
import pandas as pd

# DETALHES IMPORTANTES:
# Crie um .env no diretório GESTOR_FINANCEIRO/ com uma variável LINK_GOOGLE_SHEET, presente no próprio link da planilha, entre d/ ... (Essa parte aqui)/edit
# Lembrando que você deve compartilhar a planilha do Google Sheets com a conta do Bot do Cloud (e-mail)

load_dotenv()

class driveBot:
    def __init__(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))  # Diretório onde está o drive_bot.py
        credentials_path = os.path.join(current_dir, "../credentials.json")  # Caminho absoluto para o credentials.json
        self.gc = gspread.service_account(filename=credentials_path)
    
    def get_data(self):
        link_google_sheet = os.getenv("LINK_GOOGLE_SHEET")
        sh = self.gc.open_by_key(link_google_sheet)
        worksheet = sh.sheet1
        dataframe = pd.DataFrame(worksheet.get_all_records())
        return dataframe