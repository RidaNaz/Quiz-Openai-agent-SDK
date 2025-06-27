import os
import uuid
import chainlit as cl
from config import gemini_config
from dotenv import load_dotenv
from agents import ItemHelpers, Runner
from context import DentalAgentContext
from orchestrator_agent import triage_agent

config = gemini_config.config

@cl.on_chat_start
async def start_chat():
    # Initialize session-specific data
    cl.user_session.set("context", DentalAgentContext())
    cl.user_session.set("current_agent", triage_agent)
    cl.user_session.set("input_history", [])
    cl.user_session.set("conversation_id", uuid.uuid4().hex[:16])

    # Send welcome message
    await cl.Message(content="🦷 Welcome to Dental Clinic Assistant! How can I help you today?", author="Assistant").send()

@cl.on_message
async def handle_message(message: cl.Message):
    # Get session data
    context = cl.user_session.get("context") or DentalAgentContext()
    current_agent = cl.user_session.get("current_agent")
    input_history = cl.user_session.get("input_history")
    conversation_id = cl.user_session.get("conversation_id")

    # Add user message to history
    input_history.append({"content": message.content, "role": "user"})

    # Simple runner call without await
    result = Runner.run_streamed(
        starting_agent=current_agent,
        input=input_history,
        context=context,
        run_config=config
        )

    # Show streaming events in Chainlit UI
    await cl.Message(content="🔄 Starting agent processing...", author="System").send()

    async for event in result.stream_events():
        if event.type == "raw_response_event":
            continue
        elif event.type == "agent_updated_stream_event":
            await cl.Message(content=f"🔄 Agent updated: {event.new_agent.name}", author="System").send()
            continue
        elif event.type == "run_item_stream_event":
            if event.item.type == "tool_call_item":
                # Updated tool call handling
                tool_name = getattr(event.item, 'function_name', 'Unknown Tool')
                await cl.Message(content=f"⚙ Tool called: {tool_name}", author="System").send()
            elif event.item.type == "tool_call_output_item":
                await cl.Message(content=f"📤 Tool output: {event.item.output}", author="System").send()
            elif event.item.type == "message_output_item":
                await cl.Message(content=f"💬 Agent response: {ItemHelpers.text_message_output(event.item)}", author="Assistant").send()
            else:
                pass  # Ignore other event types

    await cl.Message(content="✅ Processing complete!", author="System").send()

    # Update session state
    cl.user_session.set("input_history", result.to_input_list())
    cl.user_session.set("current_agent", result.last_agent)

# Start the Chainlit app
if __name__ == "__main__":
    from chainlit.cli import run_chainlit
    run_chainlit("main.py")