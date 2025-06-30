from enum import Enum
from datetime import datetime
from dataclasses import dataclass, field
from typing import Optional, List

class AppointmentStatus(str, Enum):
    SCHEDULED = "Scheduled"
    CANCELLED = "Cancelled"
    COMPLETED = "Completed"

@dataclass
class Appointment:
    appointment_id: str
    date: str
    time: str
    status: AppointmentStatus
    reason: str = "Regular Checkup"
    created_at: datetime = field(default_factory=datetime.now)

@dataclass
class DentalAgentContext:
    verified: bool = False
    patient_id: Optional[str] = None
    patient_name: Optional[str] = None
    symptoms: List[str] = field(default_factory=list)
    appointments: List[Appointment] = field(default_factory=list)

    def add_appointment(self, appointment: Appointment):
        """Helper method to safely add appointments"""
        self.appointments = [a for a in self.appointments 
                           if a.appointment_id != appointment.appointment_id]
        self.appointments.append(appointment)
