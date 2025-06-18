import gspread
import datetime
from typing import Optional
from pydantic import BaseModel
from agents import function_tool
from oauth2client.service_account import ServiceAccountCredentials

# Google Sheets setup
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
client = gspread.authorize(creds)
sheet = client.open("Openai Receptionist Agent").sheet1

class SymptomData(BaseModel):
    patient_id: str
    symptom_type: str
    description: str
    severity: Optional[str] = None

@function_tool
def log_symptoms_tool(input: SymptomData) -> str:
    """Record patient symptoms in Google Sheets"""
    
    symptoms_sheet = client.open("Symptoms").sheet1
    symptoms_sheet.append_row([
        input.patient_id,
        datetime.now().isoformat(),
        input.symptom_type,
        input.description,
        input.severity
    ])
    
    return "Symptoms logged successfully"