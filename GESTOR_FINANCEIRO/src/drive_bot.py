from dotenv import load_dotenv
import gspread
import os
import pandas as pd

load_dotenv()

class driveBot:
    def __init__(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        credentials_path = os.path.join(current_dir, "../credentials.json")
        self.gc = gspread.service_account(filename=credentials_path)
    
    def get_data(self):
        link_google_sheet = os.getenv("LINK_GOOGLE_SHEET")
        sh = self.gc.open_by_key(link_google_sheet)
        worksheet = sh.sheet1
        dataframe = pd.DataFrame(worksheet.get_all_records())
        return dataframe

    def add_row(self, row_data):
        link_google_sheet = os.getenv("LINK_GOOGLE_SHEET")
        sh = self.gc.open_by_key(link_google_sheet)
        worksheet = sh.sheet1
        worksheet.append_row(row_data)  

    def update_row(self, row_index, new_data):
        link_google_sheet = os.getenv("LINK_GOOGLE_SHEET")
        sh = self.gc.open_by_key(link_google_sheet)
        worksheet = sh.sheet1
        worksheet.update(f"A{row_index + 1}:Z{row_index + 1}", [new_data])

    def delete_row(self, row_index):
        link_google_sheet = os.getenv("LINK_GOOGLE_SHEET")
        sh = self.gc.open_by_key(link_google_sheet)
        worksheet = sh.sheet1
        worksheet.delete_rows(row_index + 1)  
