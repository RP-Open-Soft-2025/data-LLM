import datetime
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field
import os
from dotenv import load_dotenv

# Import Agno framework - only Gemini
from agno.agent import Agent
from agno.models.google import Gemini

# Import configuration settings
from config import MODEL_ID, GEMINI_API_KEY

# Load environment variables from .env file
load_dotenv()


class SenderType(str, Enum):
    BOT = "bot"
    EMPLOYEE = "employee"
    HR = "hr"


class Message(BaseModel):
    timestamp: datetime.datetime = Field(
        default_factory=lambda: datetime.datetime.now(datetime.timezone.utc),
        description="Timestamp of the message",
    )
    sender_type: SenderType = Field(
        ..., description="Type of the message sender (bot, employee, or hr)"
    )
    text: str = Field(..., description="Content of the message")


class SummarizerAgent:
    def __init__(self, model=MODEL_ID):
        """Initialize the summarizer agent with Gemini model using Agno framework"""
        self.model_id = model

        # Only use Gemini model through Agno
        self.agent = Agent(
            model=Gemini(id=model, api_key=GEMINI_API_KEY),
            markdown=True,
        )

    def summarize_conversation(
        self, current_context: str, messages: List[Message]
    ) -> str:
        """
        Summarize the conversation and create an updated context using the Agno agent with Gemini

        Args:
            current_context: The existing context string
            messages: List of Message objects in the conversation

        Returns:
            str: An updated context with the conversation summary
        """
        # Format messages for the prompt
        formatted_messages = "\n".join(
            [
                f"[{msg.timestamp.strftime('%Y-%m-%d %H:%M:%S')} - {msg.sender_type.value}] {msg.text}"
                for msg in messages
            ]
        )

        # Create the prompt
        prompt = f"""
        Current Context:
        {current_context}
        
        Recent Messages:
        {formatted_messages}
        
        Please summarize these messages and integrate important information into the context.
        Create a new comprehensive context that:
        1. Retains key information from the original context
        2. Integrates important new details from the conversation
        3. Removes redundant or outdated information
        4. Focuses on employee concerns, sentiments, and key action items
        5. Is concise but comprehensive (max 500 words)
        
        New Context:
        """

        # Use the Agno agent to generate the response
        response = self.agent.message(prompt)

        # Return the response content
        return response.content.strip()


# Test function with dummy data
def test_summarizer():
    # Create a summarizer agent
    summarizer = SummarizerAgent()

    # Initial context
    initial_context = """
    Employee ID: EMP123
    Name: John Doe
    Department: Engineering
    Recent performance review: Good teamwork, meeting expectations
    Issues: Has mentioned feeling overworked during standup meetings
    """

    # Create dummy messages
    messages = [
        Message(
            timestamp=datetime.datetime(
                2025, 4, 1, 14, 30, tzinfo=datetime.timezone.utc
            ),
            sender_type=SenderType.BOT,
            text="How are you feeling about your workload this week?",
        ),
        Message(
            timestamp=datetime.datetime(
                2025, 4, 1, 14, 32, tzinfo=datetime.timezone.utc
            ),
            sender_type=SenderType.EMPLOYEE,
            text="I've been struggling with the tight deadline for Project X. I'm working overtime almost every day.",
        ),
        Message(
            timestamp=datetime.datetime(
                2025, 4, 1, 14, 34, tzinfo=datetime.timezone.utc
            ),
            sender_type=SenderType.BOT,
            text="I understand that must be difficult. Have you spoken to your manager about this?",
        ),
        Message(
            timestamp=datetime.datetime(
                2025, 4, 1, 14, 36, tzinfo=datetime.timezone.utc
            ),
            sender_type=SenderType.EMPLOYEE,
            text="Yes, but they said everyone's under pressure to deliver. I'm concerned about burnout.",
        ),
        Message(
            timestamp=datetime.datetime(
                2025, 4, 1, 14, 38, tzinfo=datetime.timezone.utc
            ),
            sender_type=SenderType.HR,
            text="John, we can schedule a meeting to discuss resource allocation for your team. Would tomorrow at 10am work?",
        ),
    ]

    # Summarize the conversation
    updated_context = summarizer.summarize_conversation(initial_context, messages)

    print("UPDATED CONTEXT:")
    print(updated_context)

    return updated_context


if __name__ == "__main__":
    test_summarizer()
