import os
from dotenv import load_dotenv
from agents import AsyncOpenAI, OpenAIChatCompletionsModel, RunConfig

class GeminiConfig:
    def __init__(self):
        load_dotenv()
        self.MODEL_NAME = "gemini-2.0-flash"
        self.GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
        self.client = AsyncOpenAI(
            api_key=self.GEMINI_API_KEY,
            base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
        )
        self.model = OpenAIChatCompletionsModel(
            model=self.MODEL_NAME,
            openai_client=self.client
        )
        self.config = RunConfig(
            model=self.model,
            model_provider=self.client,
            tracing_disabled=True
        )

# Singleton instance
gemini_config = GeminiConfig()