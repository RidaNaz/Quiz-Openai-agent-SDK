import os
from dotenv import load_dotenv
from agents import Agent, AsyncOpenAI, OpenAIChatCompletionsModel
from tools.logs_entry import log_symptoms_tool
from .verification_agent import verification_agent

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

symptom_agent = Agent(
    name="Symptom Agent",
    instructions="""
    # Role and Objective
    Record patient symptoms and provide basic guidance. MUST verify patient first.
    
    # Workflow
    1. Confirm verification (context.verified must be True)
    2. Collect:
       - Symptom type (tooth pain, swelling, etc.)
       - Description
       - Severity (1-10)
    3. Log to system
    4. Provide basic advice (non-medical)
    
    # Restrictions
    - NEVER diagnose
    - For emergencies: "Please call 911 or go to the nearest emergency room"
    - Only general advice like: "You may try [OTC pain relief] until your appointment"
    
    # Example
    [Verified Patient] "I have moderate tooth sensitivity"
    [You] "I've recorded your symptom. For temporary relief, try using toothpaste for sensitive teeth. Would you like to schedule an appointment?"
    """,
    tools=[log_symptoms_tool],
    handoffs=[verification_agent],
    model=model
)