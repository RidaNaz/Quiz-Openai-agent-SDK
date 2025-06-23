import gspread
from pydantic import BaseModel
from agents import function_tool
from oauth2client.service_account import ServiceAccountCredentials

# Google Sheets setup
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
client = gspread.authorize(creds)
sheet = client.open("Openai Receptionist Agent").sheet1

class PatientVerificationInput(BaseModel):
    name: str
    dob: str

@function_tool
async def verify_patient_tool(name: str, dob: str) -> str:
    """Verify patient identity"""
    
    records = sheet.get_all_records()

    for row in records:
        if (row["Name"].lower() == name.lower() and 
            row["DOB"] == dob):
            return "verified"
        
    return "not_found"