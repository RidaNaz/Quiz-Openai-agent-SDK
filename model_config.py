import os
from agents import AsyncOpenAI, OpenAIChatCompletionsModel, RunConfig

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
MODEL_NAME = "gemini-2.0-flash"

def get_gemini_config():
    client = AsyncOpenAI(
        api_key=GEMINI_API_KEY,
        base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
    )
    
    return RunConfig(
        model=OpenAIChatCompletionsModel(
            model=MODEL_NAME,
            openai_client=client
        ),
        model_provider=client
    )