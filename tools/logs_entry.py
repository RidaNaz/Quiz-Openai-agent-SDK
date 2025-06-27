from typing import Optional
from datetime import datetime
from pydantic import BaseModel
from agents import function_tool
from sheet_utils import get_sheet, append_row, find_patient_row

class SymptomData(BaseModel):
    patient_id: str
    symptom_type: str
    description: str
    severity: Optional[str] = None

@function_tool
async def log_symptoms_tool(input: SymptomData) -> dict:
    """Record patient symptoms in Google Sheets.
    
    Args:
        patient_id: Patient identification number
        symptom_type: Type of symptom (e.g., 'Tooth pain', 'Bleeding gums')
        description: Detailed description of symptom
        severity: Optional severity level (1-10)
        
    Returns:
        dict: {
            "status": "success" | "error",
            "message": str
        }
    """
    sheet = get_sheet()
    
    try:
        # Verify patient exists
        if not find_patient_row(sheet, input.patient_id):
            return {
                "status": "error",
                "message": "Patient not found"
            }
        
        symptom_data = {
            "Pat Num": input.patient_id,
            "Timestamp": datetime.now().isoformat(),
            "Symptom Type": input.symptom_type,
            "Symptom Description": input.description,
            "Severity": input.severity or "",
            "Actions Taken": "Logged by receptionist agent",
            "Appointment Status": "Pending review"
        }
        
        append_row(sheet, symptom_data)
        
        return {
            "status": "success",
            "message": "Symptoms logged successfully"
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error logging symptoms: {str(e)}"
        }