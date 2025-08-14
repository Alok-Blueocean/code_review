import os
from dotenv import load_dotenv

load_dotenv()

LANGCHAIN_API_KEY = os.getenv("LANGCHAIN_API_KEY")
LANGCHAIN_TRACING_V2 = os.getenv("LANGCHAIN_TRACING_V2")
LANGCHAIN_ENDPOINT = os.getenv("LANGCHAIN_ENDPOINT")
LANGCHAIN_PROJECT = os.getenv("LANGCHAIN_PROJECT")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
gemini_api_key = os.getenv("gemini_api_key")
groq_api_key = os.getenv("groq_api_key")
model_id = 'Gemma2-9b-It'