from typing import Optional
from datetime import datetime, timedelta
from pydantic import BaseModel
from agents import function_tool, RunContextWrapper
from sheet_utils import get_sheet, find_column_index, find_patient_row, append_row
from context import DentalAgentContext

class AppointmentData(BaseModel):
    date: str  # Any format
    time: str  # HH:MM or H:MM AM/PM
    reason: Optional[str] = None

def get_day_name(date_str: str) -> str:
    """Get day name from date string"""
    try:
        dt = datetime.strptime(date_str, '%Y-%m-%d')
        return dt.strftime('%A')
    except:
        return ""

def is_past_date(date_str: str) -> bool:
    """Check if date is in the past"""
    try:
        dt = datetime.strptime(date_str, '%Y-%m-%d')
        return dt.date() < datetime.now().date()
    except:
        return False

def is_weekend(date_str: str) -> bool:
    """Check if date is weekend"""
    day = get_day_name(date_str)
    return day in ['Saturday', 'Sunday']

def is_working_hours(time_str: str) -> bool:
    """Check if time is within working hours (9AM-5PM)"""
    try:
        time_obj = datetime.strptime(time_str, '%H:%M').time()
        start = datetime.strptime('09:00', '%H:%M').time()
        end = datetime.strptime('17:00', '%H:%M').time()
        return start <= time_obj <= end
    except:
        return False

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
    """Convert various date formats to YYYY-MM-DD with relative dates support"""
    date_str = date_str.lower().strip()
    today = datetime.now().date()
    
    # Handle relative dates
    if date_str == 'today':
        return today.strftime('%Y-%m-%d')
    elif date_str == 'tomorrow':
        return (today + timedelta(days=1)).strftime('%Y-%m-%d')
    elif date_str.startswith('next '):
        day_name = date_str[5:]
        try:
            days_ahead = (['monday', 'tuesday', 'wednesday', 'thursday', 
                          'friday', 'saturday', 'sunday'].index(day_name.lower()) - today.weekday()) % 7
            if days_ahead <= 0:  # If today is that day or already passed, go to next week
                days_ahead += 7
            return (today + timedelta(days=days_ahead)).strftime('%Y-%m-%d')
        except ValueError:
            pass
    
    # Handle absolute dates
    try:
        # Try parsing with year first
        for fmt in ('%Y-%m-%d', '%d/%m/%Y', '%d %b %Y', '%d %B %Y', '%b %d %Y', '%B %d %Y'):
            try:
                dt = datetime.strptime(date_str, fmt)
                return dt.strftime('%Y-%m-%d')
            except ValueError:
                continue
        
        # Try without year (default to current year)
        for fmt in ('%d %b', '%d %B', '%b %d', '%B %d'):
            try:
                dt = datetime.strptime(date_str, fmt)
                dt = dt.replace(year=today.year)
                return dt.strftime('%Y-%m-%d')
            except ValueError:
                continue
                
        return today.strftime('%Y-%m-%d')
    except Exception:
        return today.strftime('%Y-%m-%d')

@function_tool
async def create_appointment_tool(ctx: RunContextWrapper[DentalAgentContext], date: str, time: str, reason: str = "") -> dict:
    """Book a new appointment for a verified patient.
    
    Args:
        ctx: Context wrapper with patient info
        date: Appointment date in any format (including 'today', 'tomorrow')
        time: Appointment time in any format
        reason: Optional reason for appointment
        
    Returns:
        dict: {
            "status": "success" | "past_date" | "off_day" | "off_timing" | "error",
            "message": str,
            "appointment_id": Optional[str]
        }
    """
    
    sheet = get_sheet()
    patient_id = ctx.context.patient_id
    
    try:
        # Normalize date and time
        normalized_date = normalize_date(date)
        normalized_time = normalize_time(time)
        
        # Validate date and time
        if is_past_date(normalized_date):
            return {
                "status": "past_date",
                "message": "Cannot book appointment for past dates",
                "appointment_id": None
            }
            
        if is_weekend(normalized_date):
            return {
                "status": "off_day",
                "message": "Clinic is closed on weekends",
                "appointment_id": None
            }
            
        if not is_working_hours(normalized_time):
            return {
                "status": "off_timing",
                "message": "Clinic hours are 9AM to 5PM Monday to Friday",
                "appointment_id": None
            }
        
        # Check if patient exists
        row_num = find_patient_row(sheet, patient_id)
        if not row_num:
            return {
                "status": "error",
                "message": "Patient not found",
                "appointment_id": None
            }
        
        # Generate appointment ID
        app_num = f"APP-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        # Prepare appointment data
        app_data = {
            "Pat Num": patient_id,
            "App Num": app_num,
            "Appointment Date": normalized_date,
            "Appointment Time": normalized_time,
            "Appointment Status": "Scheduled",
            "Reason": reason or "Regular Checkup",
            "Timestamp": datetime.now().isoformat()
        }
        
        # Add to sheet
        append_row(sheet, app_data)
        
        # Update context
        ctx.context.appointments.append({
            "appointment_id": app_num,
            "date": normalized_date,
            "time": normalized_time,
            "status": "Scheduled",
            "reason": reason
        })
        
        return {
            "status": "success",
            "message": f"Appointment booked for {normalized_date} at {normalized_time}",
            "appointment_id": app_num
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error creating appointment: {str(e)}",
            "appointment_id": None
        }

@function_tool
async def get_appointments_tool(ctx: RunContextWrapper[DentalAgentContext]) -> dict:
    """Fetch all appointments for a patient.
    
    Args:
        ctx: Context wrapper with patient info
        
    Returns:
        dict: {
            "status": "success" | "error",
            "appointments": List[dict],
            "message": str
        }
    """
    if not ctx.context.verified or not ctx.context.patient_id:
        return {
            "status": "error",
            "appointments": [],
            "message": "Patient not verified"
        }
    
    sheet = get_sheet()
    patient_id = ctx.context.patient_id
    
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
        
        # Update context with fresh appointments
        ctx.context.appointments = patient_apps
        
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
async def update_appointment_tool(ctx: RunContextWrapper[DentalAgentContext], appointment_id: str, new_date: str, new_time: str) -> dict:
    """Update an existing appointment.
    
    Args:
        ctx: Context wrapper with patient info
        appointment_id: Appointment ID to update
        new_date: New date in any format
        new_time: New time in any format
        
    Returns:
        dict: {
            "status": "success" | "past_date" | "off_day" | "off_timing" | "error",
            "message": str
        }
    """
    if not ctx.context.verified or not ctx.context.patient_id:
        return {
            "status": "error",
            "message": "Patient not verified"
        }
    
    sheet = get_sheet()
    patient_id = ctx.context.patient_id
    
    try:
        # Normalize new date and time
        normalized_date = normalize_date(new_date)
        normalized_time = normalize_time(new_time)
        
        # Validate new date and time
        if is_past_date(normalized_date):
            return {
                "status": "past_date",
                "message": "Cannot reschedule to a past date"
            }
            
        if is_weekend(normalized_date):
            return {
                "status": "off_day",
                "message": "Clinic is closed on weekends"
            }
            
        if not is_working_hours(normalized_time):
            return {
                "status": "off_timing",
                "message": "Clinic hours are 9AM to 5PM Monday to Friday"
            }
        
        records = sheet.get_all_records()
        
        for i, row in enumerate(records, start=2):  # Rows start at 2
            if (str(row.get("Pat Num", "")).lower() == patient_id.lower() and
                str(row.get("App Num", "")).lower() == appointment_id.lower()):
                
                # Update the cells directly
                date_col = find_column_index(sheet, "Appointment Date")
                time_col = find_column_index(sheet, "Appointment Time")
                
                sheet.update_cell(i, date_col, normalized_date)
                sheet.update_cell(i, time_col, normalized_time)
                
                # Update context
                for app in ctx.context.appointments:
                    if app["appointment_id"].lower() == appointment_id.lower():
                        app["date"] = normalized_date
                        app["time"] = normalized_time
                        break
                
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
async def cancel_appointment_tool(ctx: RunContextWrapper[DentalAgentContext], appointment_id: str) -> dict:
    """Cancel an existing appointment.
    
    Args:
        ctx: Context wrapper with patient info
        appointment_id: Appointment ID to cancel
        
    Returns:
        dict: {
            "status": "success" | "error",
            "message": str
        }
    """
    if not ctx.context.verified or not ctx.context.patient_id:
        return {
            "status": "error",
            "message": "Patient not verified"
        }
    
    sheet = get_sheet()
    patient_id = ctx.context.patient_id
    
    try:
        records = sheet.get_all_records()
        
        for i, row in enumerate(records, start=2):  # Rows start at 2
            if (str(row.get("Pat Num", "")).lower() == patient_id.lower() and
                str(row.get("App Num", "")).lower() == appointment_id.lower()):
                
                status_col = find_column_index(sheet, "Appointment Status")
                sheet.update_cell(i, status_col, "Cancelled")
                
                # Update context
                ctx.context.appointments = [app for app in ctx.context.appointments 
                                          if app["appointment_id"].lower() != appointment_id.lower()]
                
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