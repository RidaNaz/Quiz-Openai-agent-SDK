import uuid
import chainlit as cl
from config import gemini_config
from agents import ItemHelpers, Runner
from context import DentalAgentContext
from run_hooks import RunLifecycleHooks
from orchestrator_agent import triage_agent
from openai.types.responses import ResponseTextDeltaEvent

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
    
    #  # Create a new message object for streaming
    c_agent = cl.Message(content="")
    await c_agent.send()
    
    msg = cl.Message(content="")
    await msg.send()

    try:
        hooks = RunLifecycleHooks()
        # Add new user message to history
        input_history.append({"role": "user", "content": message.content})

        # Process through agent system (maintaining your working delegation)
        result = Runner.run_streamed(
            starting_agent=current_agent,
            input=input_history,
            context=context,
            run_config=config,
            hooks = hooks
        )
        
        # Process streaming events
        async for event in result.stream_events():
            
            if event.type == "agent_updated_stream_event":
                c_agent.content = f"⚡ Current Agent: {event.new_agent.name}"
                await c_agent.update()
                
            # Stream the response token by token
            # if event.type == "raw_response_event" and hasattr(event.data, 'delta'):
            #     token = event.data.delta
            if event.type == "raw_response_event" and isinstance(event.data, ResponseTextDeltaEvent):
                token = event.data.delta
                await msg.stream_token(token)
            
            elif event.type == "run_item_stream_event":
                if event.item.type == "tool_call_item":
                    print("-- Tool was called")
                    
                elif event.item.type == "tool_call_output_item":
                    print(f"-- Tool output: {event.item.output}")
                
                elif event.item.type == "message_output_item":
                #    await cl.Message(
                #         content=ItemHelpers.text_message_output(event.item),
                #         author="Assistant"
                #     ).send()
                    msg.content = ItemHelpers.text_message_output(event.item)
                    await msg.update()
                else:
                    pass  # Ignore other event types
        
        print("=== Run complete ===")
        
        # Update session state
        cl.user_session.set("input_history", result.to_input_list())
        print("input_history:", result.to_input_list())
        cl.user_session.set("context", context)  # Persist updated context
        print ("context:", context)

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