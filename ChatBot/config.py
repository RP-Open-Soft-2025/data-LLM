# Configuration settings for the counseling agent
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# API Keys
# GROQ_API_KEY = "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"  # Replace with your actual API key
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")  # Load from environment variable
OPEN_AI_API_KEY = os.getenv("OPENAI_API_KEY")  # Load from environment variable

# Model settings
# MODEL_ID = "gemini-1.5-flash"  # Updated to use Gemini model
MODEL_ID = "gpt-4o"  # Updated to use Gemini model

# File paths
EMPLOYEE_DATA_PATH = (
    "emp_reports/EMP9999_report.txt"  # Updated path based on your error message
)
QUESTIONS_PDF_PATH = "Questions.pdf"  # Updated path based on your error message

# Database settings
DB_URI = "tmp/counselling_db"

# Custom system prompt (optional, set to None to use default)
CUSTOM_SYSTEM_PROMPT = None
