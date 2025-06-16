import asyncio
import uuid
from typing import List
from agents import (
    TResponseInputItem,
    MessageOutputItem,
    HandoffOutputItem,
    ToolCallItem,
    ToolCallOutputItem,
    ItemHelpers,
    Runner,
    trace
)
from triage_agent import triage_agent
from context import DentalAgentContext
from .model_config import get_gemini_config

async def run_conversation():
    config = get_gemini_config()

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