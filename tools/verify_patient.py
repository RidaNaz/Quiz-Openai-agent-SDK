from pydantic import BaseModel
from agents import function_tool, RunContextWrapper
from sheet_utils import get_sheet, normalize_date, append_row, find_patient_row
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
            "status": "verified" | "not_verified" | "patient_created" | "failed",
            "patient_id": str,
            "message": str,
            "success": bool
        }
    """
    sheet = get_sheet()
    normalized_dob = normalize_date(dob)
    
    try:
        records = sheet.get_all_records()
        
        # Check if patient exists by name
        matching_patients = []
        for row in records:
            if row["Name"].lower() == name.lower():
                matching_patients.append(row)
        
        # Handle verification cases
        if matching_patients:
            # Check if any matching patient has matching DOB
            verified_patient = None
            for patient in matching_patients:
                if normalize_date(patient["DOB"]) == normalized_dob:
                    verified_patient = patient
                    break
            
            if verified_patient:
                # Update context
                ctx.context.verified = True
                ctx.context.patient_id = str(verified_patient["Pat Num"])
                return {
                    "status": "verified",
                    "patient_id": str(verified_patient["Pat Num"]),
                    "message": f"Welcome back {name}! You're successfully verified.",
                    "success": True
                }
            else:
                ctx.context.verified = False
                return {
                    "status": "not_verified",
                    "patient_id": "",
                    "message": "The date of birth doesn't match our records. Please verify your details.",
                    "success": False
                }
        else:
            # Create new patient
            new_patient_id = f"PAT-{len(records) + 1000}"
            new_data = {
                "Name": name,
                "DOB": normalized_dob,
                "Verified": "TRUE",
                "Pat Num": new_patient_id,
            }
            
            append_row(sheet, new_data)
            
            # Update context
            ctx.context.verified = True
            ctx.context.patient_id = new_patient_id
            return {
                "status": "patient_created",
                "patient_id": new_patient_id,
                "message": f"New patient record created. Your patient ID is {new_patient_id}.",
                "success": True
            }
        
    except Exception as e:
        print(f"Tool error: {str(e)}")  # Log actual error
        return {
            "status": "failed",
            "patient_id": "",
            "message": f"Verification service error: {str(e)}",
            "success": False
        }