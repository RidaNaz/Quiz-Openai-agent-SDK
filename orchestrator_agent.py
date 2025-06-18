import os
from dotenv import load_dotenv
from clinic_agents.symptoms_agent import symptom_agent
from clinic_agents.appointment_agent import appointment_agent
from clinic_agents.verification_agent import verification_agent
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

def log_verification(patient_id: str):
    print(f"Verified patient {patient_id}")

triage_agent = Agent(
    name="Main Router",
    instructions="""Analyze the user's request and route appropriately:
    1. For identity verification → verification_agent
    2. For appointments → appointment_agent (after verification)
    3. For symptoms → symptom_agent (after verification)
    Never proceed without verification when required!""",
    handoffs=[verification_agent, symptom_agent, appointment_agent],
    model=model
)