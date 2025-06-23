import gspread
import datetime
from pydantic import BaseModel
from agents import function_tool
from typing import Optional, List
from oauth2client.service_account import ServiceAccountCredentials

# Initialize Google Sheets
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
client = gspread.authorize(creds)
sheet = client.open("Openai Receptionist Agent").sheet1

class AppointmentData(BaseModel):
    patient_id: str
    date: str  # "YYYY-MM-DD"
    time: str  # "HH:MM"
    reason: Optional[str] = None

@function_tool
async def create_appointment_tool(patient_id: str, date: str, time: str, reason: str = "") -> str:
    try:
        sheet.append_row([
            patient_id,
            date,
            time,
            reason,
            "Scheduled",
            datetime.now().isoformat()])
        return f"Appointment created for {date} at {time}"
    
    except Exception as e:
        return f"Error creating appointment: {str(e)}"

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