import os
import uuid
import asyncio
from agents import (
    TResponseInputItem,
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
from typing import List
from dotenv import load_dotenv
from triage_agent import triage_agent
from context import DentalAgentContext

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

config = RunConfig(
    model=model,
    model_provider=external_client,
    tracing_disabled=True
)

async def run_conversation():

    # Initialize context and agent
    context = DentalAgentContext()

    current_agent = triage_agent
    conversation_id = uuid.uuid4().hex[:16]
    input_history: List[TResponseInputItem] = []

    print("Dental Clinic Assistant initialized. Type 'exit' to quit.\n")

    while True:
        user_input = input("Patient: ")
        if user_input.lower() == 'exit':
            break

        with trace("Dental Clinic", group_id=conversation_id):
            # Add user message to history
            input_history.append({"content": user_input, "role": "user"})
            
            # Run the agent
            result = await Runner.run(
                agent=current_agent,
                input_items=input_history,
                context=context,
                run_config=config
            )

            # Process and display responses
            for item in result.new_items:
                if isinstance(item, MessageOutputItem):
                    print(f"Assistant: {ItemHelpers.text_message_output(item)}")
                elif isinstance(item, HandoffOutputItem):
                    print(f"-> Transferring to {item.target_agent.name}...")
                elif isinstance(item, ToolCallItem):
                    print(f"Action: {item.tool.name}")
                elif isinstance(item, ToolCallOutputItem):
                    if item.tool.name == "verify_patient_tool":
                        context.verified = (item.output == "verified")
            
            # Update conversation state
            input_history = result.to_input_list()
            current_agent = result.last_agent

if __name__ == "__main__":
    asyncio.run(run_conversation())