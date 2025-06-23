import os
import uuid
import chainlit as cl
from agents import (
    MessageOutputItem,
    HandoffOutputItem,
    ToolCallItem,
    ToolCallOutputItem,
    ItemHelpers,
    Runner,
    trace,
    AsyncOpenAI,
    OpenAIChatCompletionsModel,
    RunConfig
)
from dotenv import load_dotenv
from context import DentalAgentContext
from orchestrator_agent import triage_agent

load_dotenv()

MODEL_NAME = "gemini-2.0-flash"
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Initialize OpenAI client
external_client = AsyncOpenAI(
    api_key=GEMINI_API_KEY,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)

model = OpenAIChatCompletionsModel(
    model=MODEL_NAME,
    openai_client=external_client
)

config = RunConfig(
    model=model,
    model_provider=external_client,
    tracing_disabled=True
)

@cl.on_chat_start
async def start_chat():
    # Initialize session-specific data
    cl.user_session.set("context", DentalAgentContext())
    cl.user_session.set("current_agent", triage_agent)
    cl.user_session.set("input_history", [])
    cl.user_session.set("conversation_id", uuid.uuid4().hex[:16])

    # Send welcome message
    await cl.Message(
        content="🦷 Welcome to Dental Clinic Assistant! How can I help you today?",
        author="Assistant"
    ).send()

@cl.on_message
async def handle_message(message: cl.Message):
    # Get session data
    context = cl.user_session.get("context")
    current_agent = cl.user_session.get("current_agent")
    input_history = cl.user_session.get("input_history")
    conversation_id = cl.user_session.get("conversation_id")

    # Add user message to history
    input_history.append({"content": message.content, "role": "user"})

    # Show typing indicator
    async with cl.Step(name="Thinking", type="llm"):
        with trace("NazCare Receptionist", group_id=conversation_id):
            # Run the agent
            result = Runner.run_streamed(
                starting_agent=current_agent,
                input=input_history,
                context=context,
                run_config=config
            )

            # Process responses
            for item in result.new_items:
                if isinstance(item, MessageOutputItem):
                    await cl.Message(
                        content=ItemHelpers.text_message_output(item),
                        author="Assistant"
                    ).send()
                elif isinstance(item, HandoffOutputItem):
                    await cl.Message(
                        content=f"→ Transferring to {item.target_agent.name}...",
                        author="System"
                    ).send()
                elif isinstance(item, ToolCallItem):
                    await cl.Message(
                        content=f"⚙️ Action: {item.tool.name}",
                        author="System"
                    ).send()
                elif isinstance(item, ToolCallOutputItem):
                    if item.tool.name == "verify_patient_tool":
                        context.verified = (item.output == "verified")

        # Update session state
        cl.user_session.set("input_history", result.to_input_list())
        cl.user_session.set("current_agent", result.last_agent)

# Start the Chainlit app
if __name__ == "__main__":
    from chainlit.cli import run_chainlit
    run_chainlit("main.py")