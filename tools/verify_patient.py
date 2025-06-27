from pydantic import BaseModel
from agents import function_tool, RunContextWrapper
from sheet_utils import get_sheet, normalize_date, find_column_index, append_row
from context import DentalAgentContext

class PatientVerificationInput(BaseModel):
    name: str
    dob: str

@function_tool
async def verify_patient_tool(ctx: RunContextWrapper[DentalAgentContext], name: str, dob: str) -> dict:
    """Verify patient identity or create new record if not found.
    
    Args:
        ctx: Context wrapper for maintaining state (must be first parameter)
        name: Full patient name
        dob: Date of birth in any format (e.g., 16 Sep 2002, 09/16/2002)
        
    Returns:
        dict: {
            "status": "verified" | "created" | "failed",
            "patient_id": str,
            "message": str
        }
    """
    sheet = get_sheet()
    normalized_dob = normalize_date(dob)
    status = ""
    patient_id = ""
    
    try:
        records = sheet.get_all_records()
        
        # Check for existing patient
        for row in records:
            if (row["Name"].lower() == name.lower() and 
                normalize_date(row["DOB"]) == normalized_dob):
                status = "verified"
                patient_id = str(row["Pat Num"])
                message = "Patient verified successfully"
                break
        
        # Create new patient if not found
        if not status:
            new_patient_id = f"PAT-{len(records) + 1000}"
            new_data = {
                "Name": name,
                "DOB": normalized_dob,
                "Verified": "TRUE",
                "Pat Num": new_patient_id,
            }
            
            append_row(sheet, new_data)
            status = "created"
            patient_id = new_patient_id
            message = "New patient record created"
        
        # Update context if verification succeeded
        if status in ["verified", "created"]:
            ctx.context.verified = True
            ctx.context.patient_id = patient_id
        
        return {
            "status": status,
            "patient_id": patient_id,
            "message": message,
            "context": ctx.context
        }
        
    except Exception as e:
        return {
            "status": "failed",
            "patient_id": "",
            "message": f"Error: {str(e)}"
        }