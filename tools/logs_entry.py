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