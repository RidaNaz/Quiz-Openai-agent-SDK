from enum import Enum
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field

class AppointmentStatus(str, Enum):
    SCHEDULED = "Scheduled"
    CANCELLED = "Cancelled"
    COMPLETED = "Completed"

class Appointment(BaseModel):
    appointment_id: str
    date: str  # YYYY-MM-DD format
    time: str  # HH:MM format
    status: AppointmentStatus
    reason: str = "Regular Checkup"
    created_at: datetime = Field(default_factory=datetime.now)

class DentalAgentContext(BaseModel):
    verified: bool = False
    patient_id: Optional[str] = None
    patient_name: Optional[str] = None
    symptoms: List[str] = []
    appointments: List[Appointment] = []
    current_action: Optional[str] = None
    last_verified: Optional[datetime] = None

    def add_appointment(self, appointment: Appointment):
        """Helper method to safely add appointments"""
        self.appointments = [a for a in self.appointments 
                           if a.appointment_id != appointment.appointment_id]
        self.appointments.append(appointment)