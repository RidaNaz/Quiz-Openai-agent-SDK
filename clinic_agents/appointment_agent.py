from agents import Agent
from tools.appointments import (
    get_appointments_tool,
    create_appointment_tool,
    update_appointment_tool,
    cancel_appointment_tool
)
from tools.send_email import send_email_tool
from .verification_agent import verification_agent
from ..model_config import get_gemini_config

appointment_agent = Agent(
    name="Appointment Agent",
    instructions="""Handle all appointment operations. Verify patient first if needed.
    Available actions:
    - Check existing appointments
    - Book new appointments
    - Reschedule appointments
    - Cancel appointments""",
    tools=[
        get_appointments_tool,
        create_appointment_tool,
        update_appointment_tool,
        cancel_appointment_tool,
        send_email_tool
    ],
    handoffs=[verification_agent],
    model=get_gemini_config().model.model_name,  # "gemini-2.0-flash"
    model_settings={
        "temperature": 0.3,
        "max_tokens": 150
    }
)