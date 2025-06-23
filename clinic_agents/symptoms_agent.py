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
    instructions="""Record patient symptoms and provide basic advice.
    Required verification before logging any symptoms.""",
    tools=[log_symptoms_tool],
    handoffs=[verification_agent],
    model=model
)