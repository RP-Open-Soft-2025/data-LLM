"""Configuration for the employee analysis system."""

import os
from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI
from openai import OpenAI
from dotenv import load_dotenv
load_dotenv()
# Default model configuration
DEFAULT_MODEL = "llama3-70b-8192"  # You can choose a suitable Groq model
DEFAULT_TEMPERATURE = 0.2

# Initialize LLM
def get_llm(model_name=None, temperature=None):
    """Get the LLM instance based on configuration."""
    model = model_name or os.getenv("GROQ_MODEL", DEFAULT_MODEL)
    temp = temperature if temperature is not None else float(os.getenv("LLM_TEMPERATURE", DEFAULT_TEMPERATURE))
    
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    model='gpt-4o-mini'
    return ChatOpenAI(
        api_key=os.getenv("OPENAI_API_KEY"),
        model_name=model,
        temperature=temp,
        max_retries=2
    )
