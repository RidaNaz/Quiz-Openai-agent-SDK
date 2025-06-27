import os
from dotenv import load_dotenv
from tools.appointments import (
    get_appointments_tool,
    create_appointment_tool,
    update_appointment_tool,
    cancel_appointment_tool
)
from tools.send_email import send_email_tool
from .verification_agent import verification_agent
from agents import Agent, AsyncOpenAI, OpenAIChatCompletionsModel

load_dotenv()

MODEL_NAME = "gemini-2.0-flash"
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

external_client = AsyncOpenAI(
    api_key=GEMINI_API_KEY,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)

model = OpenAIChatCompletionsModel(
    model=MODEL_NAME,
    openai_client=external_client
)

appointment_agent = Agent(
    name="Appointment Agent",
    instructions="""
    # Role and Objective
    Handle all appointment operations. Strict verification required.
    
    # Appointment Rules
    - Hours: Monday-Friday, 9AM-5PM
    - Minimum notice: 24 hours
    - Cancellation policy: 48-hour notice
    
    # Workflows
    1. CHECK APPOINTMENTS:
       - List all upcoming appointments
       - Include date, time, and reason
    
    2. BOOK APPOINTMENT:
       - Verify availability
       - Confirm details before booking
       - Send confirmation email
    
    3. UPDATE APPOINTMENT:
       - Verify new slot availability
       - Confirm changes
       - Send update email
    
    4. CANCEL APPOINTMENT:
       - Confirm cancellation
       - Note reason if provided
       - Send cancellation email
    
    # Communication
    - Always confirm details: "You're booking for [date] at [time], correct?"
    - For conflicts: "That time isn't available. The next opening is..."
    - After actions: "I've [action] your appointment. You'll receive a confirmation email."
    
    # Example
    [Verified Patient] "I need to reschedule my appointment"
    [You] "Let me check availability. What new date and time would you prefer?"
    """,
    tools=[
        get_appointments_tool,
        create_appointment_tool,
        update_appointment_tool,
        cancel_appointment_tool,
        send_email_tool
    ],
    handoffs=[verification_agent],
    model=model
)