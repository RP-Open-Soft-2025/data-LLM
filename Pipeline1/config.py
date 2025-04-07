"""Configuration for the employee analysis system."""

import os
from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI
# from langchain_google_genai import ChatGoogleGenerativeAI
# from openai import OpenAI
from dotenv import load_dotenv
load_dotenv()
# Default model configuration
DEFAULT_MODEL = "gpt-4o-mini"  # You can choose a suitable Groq model
DEFAULT_TEMPERATURE = 0.2

# Initialize LLM
def get_llm(model_name=None, temperature=None):
    """Get the LLM instance based on configuration."""
    model = model_name
    temp = temperature if temperature is not None else float(os.getenv("LLM_TEMPERATURE", DEFAULT_TEMPERATURE))
    
    # client = OpenAI(api_key=os.getenv("GEMINI_API_KEY"))
    model='gpt-4o-mini'
    return ChatOpenAI(
        api_key=os.getenv("OPEN_AI_API_KEY"),
        model=model,
        temperature=temp,
        max_retries=2
    )
