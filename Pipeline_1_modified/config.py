"""Configuration for the employee analysis system."""

import os
from langchain_groq import ChatGroq

# Default model configuration
DEFAULT_MODEL = "llama3-70b-8192"  # You can choose a suitable Groq model
DEFAULT_TEMPERATURE = 0.2


# Initialize LLM
def get_llm(model_name=None, temperature=None):
    """Get the LLM instance based on configuration."""
    model = model_name or os.getenv("GROQ_MODEL", DEFAULT_MODEL)
    temp = (
        temperature
        if temperature is not None
        else float(os.getenv("LLM_TEMPERATURE", DEFAULT_TEMPERATURE))
    )

    return ChatGroq(
        model=model,
        temperature=temp,
        max_tokens=None,
        timeout=None,
        max_retries=2,
        api_key=os.getenv(
            "GROQ_API_KEY", "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"
        ),
    )
