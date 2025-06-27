from typing import Optional
from datetime import datetime
from pydantic import BaseModel
from agents import function_tool
from sheet_utils import get_sheet, find_column_index, find_patient_row, append_row

class AppointmentData(BaseModel):
    patient_id: str
    date: str  # Any format
    time: str  # HH:MM or H:MM AM/PM
    reason: Optional[str] = None

def normalize_time(time_str: str) -> str:
    """Convert various time formats to HH:MM"""
    try:
        # Try parsing with AM/PM
        for fmt in ('%I:%M %p', '%I %p', '%H:%M'):
            try:
                dt = datetime.strptime(time_str, fmt)
                return dt.strftime('%H:%M')
            except ValueError:
                continue
        return "09:00"  # Default time
    except Exception:
        return "09:00"

def normalize_date(date_str: str) -> str:
    """Convert various date formats to YYYY-MM-DD with default year 2025"""
    try:
        # Try parsing with year first
        for fmt in ('%Y-%m-%d', '%d/%m/%Y', '%d %b %Y', '%d %B %Y', '%b %d %Y', '%B %d %Y'):
            try:
                dt = datetime.strptime(date_str, fmt)
                return dt.strftime('%Y-%m-%d')
            except ValueError:
                continue
        
        # Try without year (default to 2025)
        for fmt in ('%d %b', '%d %B', '%b %d', '%B %d'):
            try:
                dt = datetime.strptime(date_str, fmt)
                dt = dt.replace(year=2025)  # Default year set to 2025
                return dt.strftime('%Y-%m-%d')
            except ValueError:
                continue
                
        return datetime.now().strftime('%Y-%m-%d')
    except Exception:
        return datetime.now().strftime('%Y-%m-%d')

@function_tool
async def create_appointment_tool(patient_id: str, date: str, time: str, reason: str = "") -> dict:
    """Book a new appointment for a verified patient.
    
    Args:
        patient_id: Patient identification number
        date: Appointment date in any format
        time: Appointment time in any format
        reason: Optional reason for appointment
        
    Returns:
        dict: {
            "status": "success" | "error",
            "message": str,
            "appointment_id": Optional[str]
        }
    """
    sheet = get_sheet()
    
    try:
        row_num = find_patient_row(sheet, patient_id)
        if not row_num:
            return {
                "status": "error",
                "message": "Patient not found",
                "appointment_id": None
            }
        
        app_num = f"APP-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        normalized_date = normalize_date(date)
        normalized_time = normalize_time(time)
        
        app_data = {
            "Pat Num": patient_id,
            "App Num": app_num,
            "Appointment Date": normalized_date,
            "Appointment Time": normalized_time,
            "Appointment Status": "Scheduled",
            "Reason": reason or "",
            "Timestamp": datetime.now().isoformat()
        }
        
        append_row(sheet, app_data)
        
        return {
            "status": "success",
            "message": f"Appointment created for {normalized_date} at {normalized_time}",
            "appointment_id": app_num
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error creating appointment: {str(e)}",
            "appointment_id": None
        }

@function_tool
async def get_appointments_tool(patient_id: str) -> dict:
    """Fetch all appointments for a patient.
    
    Args:
        patient_id: Patient identification number
        
    Returns:
        dict: {
            "status": "success" | "error",
            "appointments": List[dict],
            "message": str
        }
    """
    sheet = get_sheet()
    
    try:
        records = sheet.get_all_records()
        patient_apps = []
        
        for row in records:
            if str(row.get("Pat Num", "")).lower() == patient_id.lower():
                if row.get("Appointment Status", "").lower() not in ["cancelled", "completed"]:
                    patient_apps.append({
                        "appointment_id": row.get("App Num", ""),
                        "date": row.get("Appointment Date", ""),
                        "time": row.get("Appointment Time", ""),
                        "status": row.get("Appointment Status", ""),
                        "reason": row.get("Reason", "")
                    })
        
        return {
            "status": "success",
            "appointments": patient_apps,
            "message": f"Found {len(patient_apps)} appointments"
        }
        
    except Exception as e:
        return {
            "status": "error",
            "appointments": [],
            "message": f"Error fetching appointments: {str(e)}"
        }

@function_tool
async def update_appointment_tool(patient_id: str, appointment_id: str, new_date: str, new_time: str) -> dict:
    """Update an existing appointment.
    
    Args:
        patient_id: Patient identification number
        appointment_id: Appointment ID to update
        new_date: New date in any format
        new_time: New time in any format
        
    Returns:
        dict: {
            "status": "success" | "error",
            "message": str
        }
    """
    sheet = get_sheet()
    
    try:
        records = sheet.get_all_records()
        normalized_date = normalize_date(new_date)
        normalized_time = normalize_time(new_time)
        
        for i, row in enumerate(records, start=2):  # Rows start at 2
            if (str(row.get("Pat Num", "")).lower() == patient_id.lower() and
                str(row.get("App Num", "")).lower() == appointment_id.lower()):
                
                # Update the cells directly
                date_col = find_column_index(sheet, "Appointment Date")
                time_col = find_column_index(sheet, "Appointment Time")
                
                sheet.update_cell(i, date_col, normalized_date)
                sheet.update_cell(i, time_col, normalized_time)
                
                return {
                    "status": "success",
                    "message": f"Appointment updated to {normalized_date} at {normalized_time}"
                }
        
        return {
            "status": "error",
            "message": "Appointment not found"
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error updating appointment: {str(e)}"
        }

@function_tool
async def cancel_appointment_tool(patient_id: str, appointment_id: str) -> dict:
    """Cancel an existing appointment.
    
    Args:
        patient_id: Patient identification number
        appointment_id: Appointment ID to cancel
        
    Returns:
        dict: {
            "status": "success" | "error",
            "message": str
        }
    """
    sheet = get_sheet()
    
    try:
        records = sheet.get_all_records()
        
        for i, row in enumerate(records, start=2):  # Rows start at 2
            if (str(row.get("Pat Num", "")).lower() == patient_id.lower() and
                str(row.get("App Num", "")).lower() == appointment_id.lower()):
                
                status_col = find_column_index(sheet, "Appointment Status")
                sheet.update_cell(i, status_col, "Cancelled")
                
                return {
                    "status": "success",
                    "message": "Appointment cancelled successfully"
                }
        
        return {
            "status": "error",
            "message": "Appointment not found"
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error cancelling appointment: {str(e)}"
        }