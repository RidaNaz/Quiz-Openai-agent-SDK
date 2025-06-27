import gspread
from datetime import datetime
from typing import Dict, Optional
from oauth2client.service_account import ServiceAccountCredentials

# Initialize Google Sheets client
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
client = gspread.authorize(creds)

def get_sheet():
    return client.open("Openai Receptionist Agent").sheet1

def normalize_date(date_str: str) -> str:
    """Convert various date formats to YYYY-MM-DD"""
    try:
        # Try common formats
        for fmt in ('%Y-%m-%d', '%d/%m/%Y', '%m/%d/%Y', '%d-%b-%Y', '%d %b %Y', '%b %d %Y'):
            try:
                dt = datetime.strptime(date_str, fmt)
                return dt.strftime('%Y-%m-%d')
            except ValueError:
                continue
        # Fallback to current date if parsing fails
        return datetime.now().strftime('%Y-%m-%d')
    except Exception:
        return datetime.now().strftime('%Y-%m-%d')

def find_column_index(sheet, column_name: str) -> int:
    """Find column index by name (case-insensitive)"""
    header = sheet.row_values(1)
    for idx, col in enumerate(header):
        if col.lower() == column_name.lower():
            return idx + 1  # Sheets are 1-indexed
    raise ValueError(f"Column '{column_name}' not found in sheet")

def append_row(sheet, data: Dict[str, str]) -> None:
    """Append a row with data mapped to correct columns"""
    header = sheet.row_values(1)
    row = [""] * len(header)
    
    for key, value in data.items():
        try:
            col_idx = find_column_index(sheet, key)
            row[col_idx - 1] = value  # Convert to 0-based index
        except ValueError:
            continue  # Skip if column not found
    
    sheet.append_row(row)

def find_patient_row(sheet, patient_id: str) -> Optional[int]:
    """Find row number by patient ID"""
    pat_num_col = find_column_index(sheet, "Pat Num")
    records = sheet.get_all_records()
    
    for i, row in enumerate(records, start=2):  # Start from row 2 (1 is header)
        if str(row.get("Pat Num", "")).lower() == patient_id.lower():
            return i
    return None