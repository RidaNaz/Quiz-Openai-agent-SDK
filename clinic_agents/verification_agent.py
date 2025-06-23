import os
from dotenv import load_dotenv
from context import DentalAgentContext
from tools.verify_patient import verify_patient_tool
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

verification_agent = Agent[DentalAgentContext](
    name="Verification Agent",
    instructions="Verify patient identity using name and DOB",
    tools=[verify_patient_tool],
    model=model
)