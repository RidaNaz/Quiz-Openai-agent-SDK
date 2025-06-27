import os
import uuid
import chainlit as cl
from datetime import datetime
from config import gemini_config
from agents import ItemHelpers, Runner
from context import DentalAgentContext
from orchestrator_agent import triage_agent

config = gemini_config.config

@cl.on_chat_start
async def start_chat():
    """Initialize a new chat session with clean state."""
    # Initialize fresh context and history
    initial_context = DentalAgentContext()
    
    # Set session state
    cl.user_session.set("context", initial_context)
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
    """Process incoming messages through the agent system."""
    # Retrieve session state
    context = cl.user_session.get("context", DentalAgentContext())
    current_agent = cl.user_session.get("current_agent", triage_agent)
    input_history = cl.user_session.get("input_history", [])
    conversation_id = cl.user_session.get("conversation_id", "unknown")

    try:
        # Add new user message to history
        input_history.append({"role": "user", "content": message.content})

        # Process through agent system (maintaining your working delegation)
        result = Runner.run_streamed(
            starting_agent=current_agent,
            input=input_history,
            context=context,
            run_config=config
        )

        # Track verification updates
        last_tool_called = None
        
        # Process streaming events
        async for event in result.stream_events():
            if event.type == "raw_response_event":
                continue
                
            elif event.type == "agent_updated_stream_event":
                await cl.Message(
                    content=f"⚡ Agent changed to: {event.new_agent.name}",
                    author="System"
                ).send()
                
            elif event.type == "run_item_stream_event":
                if event.item.type == "tool_call_item":
                    last_tool_called = getattr(event.item, 'function_name', None)
                    await cl.Message(
                        content=f"⚙ Executing: {last_tool_called}",
                        author="System"
                    ).send()
                    
                elif event.item.type == "tool_call_output_item":
                    # Update context only for successful verification
                    if last_tool_called == "verify_patient_tool":
                        if event.item.output.get("status") in ["verified", "created"]:
                            context.verified = True
                            context.patient_id = event.item.output.get("patient_id")
                
                elif event.item.type == "message_output_item":
                    await cl.Message(
                        content=ItemHelpers.text_message_output(event.item),
                        author="Assistant"
                    ).send()

        # Update session state
        cl.user_session.set("input_history", result.to_input_list())
        cl.user_session.set("current_agent", result.last_agent)
        cl.user_session.set("context", context)  # Persist updated context

    except Exception as e:
        # Handle errors gracefully
        error_msg = "⚠️ Please try again or contact support if the issue persists."
        await cl.Message(content=error_msg, author="System").send()
        
        # Log error with conversation ID
        print(f"Error in conversation {conversation_id}: {str(e)}")
        
        # Reset to triage agent but maintain history
        cl.user_session.set("current_agent", triage_agent)

if __name__ == "__main__":
    from chainlit.cli import run_chainlit
    run_chainlit("main.py")