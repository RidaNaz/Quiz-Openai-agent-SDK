from dataclasses import dataclass
from typing import Optional

@dataclass
class DentalAgentContext:
    verified: bool = False
    patient_id: Optional[str] = None
    current_patient_name: Optional[str] = None