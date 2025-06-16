from typing import Optional, List
from pydantic import BaseModel
from agents import function_tool
import gspread
import datetime
from oauth2client.service_account import ServiceAccountCredentials

# Initialize Google Sheets
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
client = gspread.authorize(creds)

class AppointmentData(BaseModel):
    patient_id: str
    date: str  # "YYYY-MM-DD"
    time: str  # "HH:MM"
    reason: Optional[str] = None

@function_tool
def create_appointment_tool(input: AppointmentData) -> str:
    """Create new appointment in Google Sheets"""
    sheet = client.open("Appointments").sheet1
    sheet.append_row([
        input.patient_id,
        input.date,
        input.time,
        input.reason or "",
        "Scheduled",
        datetime.now().isoformat()
    ])
    return f"Appointment created for {input.date} at {input.time}"

@function_tool
def get_appointments_tool(patient_id: str) -> List[dict]:
    """Fetch all appointments for a patient"""
    records = client.open("Appointments").sheet1.get_all_records()
    return [r for r in records if r["PatientID"] == patient_id]

@function_tool
def update_appointment_tool(patient_id: str, new_date: str, new_time: str) -> str:
    """Update existing appointment"""
    sheet = client.open("Appointments").sheet1
    # Implementation to find and update record
    return f"Updated to {new_date} {new_time}"

@function_tool
def cancel_appointment_tool(patient_id: str) -> str:
    """Cancel an appointment"""
    sheet = client.open("Appointments").sheet1
    # Implementation to mark as cancelled
    return "Appointment cancelled"