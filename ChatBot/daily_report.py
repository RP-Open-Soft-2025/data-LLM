import datetime
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field
import os
from dotenv import load_dotenv

# Import Agno framework - only Gemini
from agno.agent import Agent

# from agno.models.google import OpenAIChat
from agno.models.openai import OpenAIChat

# Import configuration settings
from .config import MODEL_ID, OPEN_AI_API_KEY

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


class DailyReportAgent:
    def __init__(self, model=MODEL_ID):
        """Initialize the summarizer agent with model using Agno framework"""
        self.model_id = model

        # Agent description for context
        self.description = """
        You are a professional mental health report writer who creates concise, 
        objective summaries of counseling sessions for HR departments. Your reports 
        help HR professionals understand employee well-being concerns while maintaining 
        appropriate confidentiality and professional standards.
        """

        # Agent instructions for behavior and tone
        self.instructions = [
            "Focus on factual information and avoid subjective judgments",
            "Present employee concerns in a balanced and fair manner",
            "Highlight key action items and follow-ups needed by HR",
            "Use professional but empathetic language",
            "Organize information into clear, structured sections",
            "Maintain confidentiality while providing necessary context",
            "Identify patterns or recurring themes in employee concerns",
            "Flag urgent issues requiring immediate attention",
        ]

        # Create the agent with description and instructions
        self.agent = Agent(
            model=OpenAIChat(id=model, api_key=OPEN_AI_API_KEY),
            description=self.description,
            instructions=self.instructions,
            markdown=True,
        )

    def generate_daily_report(
        self, current_context: str, messages: List[Message]
    ) -> str:
        """
        Summarize the counseling conversation and create a report for HR using the Agno agent

        Args:
            current_context: The existing context about the employee
            messages: List of Message objects in the conversation between employee and counseling bot

        Returns:
            str: A structured report on the counseling conversation
        """
        # Format messages for the prompt
        formatted_messages = "\n".join(
            [
                f"[{msg.timestamp.strftime('%Y-%m-%d %H:%M:%S')} - {msg.sender_type.value}] {msg.text}"
                for msg in messages
            ]
        )

        # Create the prompt with specific guidance for counseling context
        prompt = f"""
        You are tasked with generating a professional counseling summary report based on the following:

        Employee Context:
        {current_context}

        Counseling Session Messages:
        {formatted_messages}

        Please create a detailed counseling report that:
        1. Summarizes the key points from the counseling conversation
        2. Identifies main concerns, stressors, or challenges the employee is facing
        3. Highlights any mental health or well-being issues that should be noted
        4. Documents any workplace-related issues mentioned (workload, team dynamics, etc.)
        5. Notes any follow-up actions suggested during the conversation
        6. Assesses urgency level of concerns (if any require immediate HR attention)
        7. Organizes information into clearly labeled sections (e.g., Summary, Key Concerns, Recommendations, Follow-up Items)
        8. Uses professional, objective, and empathetic language
        9. Remains factual and avoids speculation
        10. Respects employee confidentiality while providing necessary context for HR

        This report will be reviewed by HR personnel to ensure appropriate support for the employee.
        """

        # Use the Agno agent to generate the response
        response = self.agent.run(prompt)

        # Return the response content
        return response.content.strip()


# Test function with dummy data
def test_summarizer():
    # Create a summarizer agent
    summarizer = DailyReportAgent()

    # Initial context
    initial_context = """
    Employee ID: EMP123
    Name: John Doe
    Department: Engineering
    Recent performance review: Good teamwork, meeting expectations
    Previous counseling notes: Has mentioned feeling overwhelmed and anxious about project deadlines
    """

    # Create dummy messages
    messages = [
        Message(
            timestamp=datetime.datetime(
                2025, 4, 1, 14, 30, tzinfo=datetime.timezone.utc
            ),
            sender_type=SenderType.BOT,
            text="How have you been managing your stress levels since we last spoke?",
        ),
        Message(
            timestamp=datetime.datetime(
                2025, 4, 1, 14, 32, tzinfo=datetime.timezone.utc
            ),
            sender_type=SenderType.EMPLOYEE,
            text="Not great. I've been having trouble sleeping and find myself worrying constantly about Project X deadlines. I'm feeling overwhelmed most days.",
        ),
        Message(
            timestamp=datetime.datetime(
                2025, 4, 1, 14, 34, tzinfo=datetime.timezone.utc
            ),
            sender_type=SenderType.BOT,
            text="I'm sorry to hear that. Have you been able to use any of the coping strategies we discussed last time?",
        ),
        Message(
            timestamp=datetime.datetime(
                2025, 4, 1, 14, 36, tzinfo=datetime.timezone.utc
            ),
            sender_type=SenderType.EMPLOYEE,
            text="I tried the breathing exercises, but it's hard to find time. My manager keeps adding more tasks and doesn't seem to understand when I say I'm at capacity.",
        ),
        Message(
            timestamp=datetime.datetime(
                2025, 4, 1, 14, 38, tzinfo=datetime.timezone.utc
            ),
            sender_type=SenderType.HR,
            text="John, we appreciate you sharing these concerns. Would you like to schedule a confidential meeting with HR to discuss workload management options?",
        ),
    ]

    # Summarize the conversation
    updated_context = summarizer.generate_daily_report(initial_context, messages)

    print("COUNSELING REPORT:")
    print(updated_context)

    # Save the report to a file in the daily_reports folder
    save_to_file(updated_context)

    return updated_context


def save_to_file(report_content):
    """
    Save the report to a file in the daily_reports folder

    Args:
        report_content: The report content to save
    """
    # Create daily_reports directory outside the ChatBot folder
    reports_dir = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "daily_reports"
    )

    # Create the directory if it doesn't exist
    if not os.path.exists(reports_dir):
        os.makedirs(reports_dir)

    # Create a filename with the current timestamp
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"report_{timestamp}.md"

    # Complete path to save the file
    file_path = os.path.join(reports_dir, filename)

    # Save the report content to the file
    with open(file_path, "w") as file:
        file.write(report_content)

    print(f"Report saved to: {file_path}")


if __name__ == "__main__":
    test_summarizer()
