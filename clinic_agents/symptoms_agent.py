from agents import Agent
from tools.logs_entry import log_symptoms_tool
from .verification_agent import verification_agent
from ..model_config import get_gemini_config

symptom_agent = Agent(
    name="Symptom Agent",
    instructions="""Record patient symptoms and provide basic advice.
    Required verification before logging any symptoms.""",
    tools=[log_symptoms_tool],
    handoffs=[verification_agent],
    model=get_gemini_config().model.model_name,  # "gemini-2.0-flash"
    model_settings={
        "temperature": 0.3,
        "max_tokens": 150
    }
)