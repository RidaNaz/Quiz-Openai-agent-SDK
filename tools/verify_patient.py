from typing import Optional
from pydantic import BaseModel
from agents import function_tool
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Google Sheets setup
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
client = gspread.authorize(creds)
sheet = client.open("Patient Records").sheet1

class PatientVerificationInput(BaseModel):
    name: str
    dob: str  # Format: "YYYY-MM-DD"

@function_tool
def verify_patient_tool(input: PatientVerificationInput) -> str:
    """Verify patient identity against Google Sheets records.
    Returns 'verified' or 'not_found'"""
    
    records = sheet.get_all_records()
    for row in records:
        if (row["Name"].lower() == input.name.lower() and 
            row["DOB"] == input.dob):
            return "verified"
    
    return "not_found"