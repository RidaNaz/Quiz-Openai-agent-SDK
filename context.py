from datetime import datetime
from pydantic import BaseModel
from typing import Optional, List

class DentalAgentContext(BaseModel):
    verified: bool = False
    patient_id: Optional[str] = None
    symptoms: List[str] = []
    appointments: List[dict] = []
    current_action: Optional[str] = None
    
    def copy(self):
        return self.__class__(**self.dict())