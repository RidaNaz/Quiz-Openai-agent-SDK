from agents import Agent, handoff
from agents.extensions import handoff_filters
from .verification_agent import verification_agent
from .appointment_agent import appointment_agent
from .symptoms_agent import symptom_agent
from ..model_config import get_gemini_config

def log_verification(patient_id: str):
    print(f"Verified patient {patient_id}")

# Secure handoff configuration
secured_appointment_handoff = handoff(
    agent=appointment_agent,
    input_filter=handoff_filters.require_verified_context,
    on_handoff=lambda ctx: log_verification(ctx.get("patient_id", "unknown"))
)

secured_symptom_handoff = handoff(
    agent=symptom_agent,
    input_filter=handoff_filters.require_verified_context
)

router_agent = Agent(
    name="Main Router",
    instructions="""Analyze the user's request and route appropriately:
    1. For identity verification → verification_agent
    2. For appointments → appointment_agent (after verification)
    3. For symptoms → symptom_agent (after verification)
    Never proceed without verification when required!""",
    handoffs=[verification_agent, secured_appointment_handoff, secured_symptom_handoff],
    model=get_gemini_config().model.model_name,  # "gemini-2.0-flash"
    model_settings={
        "temperature": 0.3,
        "max_tokens": 150
    }
)