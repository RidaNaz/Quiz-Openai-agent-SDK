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
    model=model
)