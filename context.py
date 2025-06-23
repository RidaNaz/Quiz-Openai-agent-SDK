from datetime import datetime
from pydantic import BaseModel
from typing import Optional, List

class DentalAgentContext(BaseModel):
    patient_id: Optional[str] = None
    verified: bool = False
    verification_time: Optional[datetime] = None
    symptoms: List[str] = []
    appointments: List[dict] = []
    current_action: Optional[str] = None