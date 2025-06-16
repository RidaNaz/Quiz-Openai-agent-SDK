from agents import Agent
from ..tools.verify_patient import verify_patient_tool
from context import DentalAgentContext
from ..model_config import get_gemini_config

verification_agent = Agent[DentalAgentContext](
    name="Verification Agent",
    instructions="Verify patient identity using name and DOB",
    tools=[verify_patient_tool],
    model=get_gemini_config().model.model_name,  # "gemini-2.0-flash"
    model_settings={
        "temperature": 0.3,
        "max_tokens": 150
    }
)