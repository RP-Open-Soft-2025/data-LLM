from agno.agent import Agent
from agno.models.openai import OpenAIChat
from typing import List, Dict
import os
from dotenv import load_dotenv
from . import config

# Load environment variables from .env file
load_dotenv()

class EmpathizerAgent:
    def __init__(self, model_id=config.MODEL_ID):
        """
        Initialize the empathizer agent with a lightweight model using Groq.
        
        Args:
            model_id: ID of the LLM to use (default: llama3-8b-8192 which is less powerful but fast)
        """
        
        # Get Groq API key
        api_key = config.OPEN_AI_API_KEY
        model = OpenAIChat(id=model_id, api_key=api_key)
        
        # Agent description for context
        description = """
        You are an empathetic response generator who creates warm, encouraging, and supportive
        responses for a counseling chatbot. Your job is to acknowledge the employee's feelings
        and create a safe space for them to share their thoughts.
        """
        
        # Instructions for the agent
        instructions = [
            "Make sure to generate something ONLY if empathy is needed",
            "If empathy is not really required, if the employee is not expressing any strong emotions, don't generate anything.",
            "Try to keep making the responses creative and unique",
            "Don't repeat the same phrases or words in multiple responses, make sure, no two responses start with the same kind of words (e.g. It sounds like)",
            "Generate short, empathetic responses (1 sentence only)",
            "Your response must be at most 13 words long"
            "Acknowledge the emotions expressed by the employee in their recent messages",
            "Provide ONLY the actual text you would say to the employee without any metadata.",
            "Do NOT include any surrounding punctuation or formatting (e.g. NO surrounding inverted commas)",
            "Use warm, supportive language that shows understanding",
            "Avoid clichés and generic statements",
            "Keep responses concise and focused",
            "Don't offer solutions or advice - just empathize, that too ONLY if it is needed",
            "Match the emotional tone of the conversation",
            "Use natural, conversational language",
        ]
        
        # Create the agent with a lightweight model
        self.agent = Agent(
            model=model,
            description=description,
            instructions=instructions,
            markdown=True,
        )
    
    def generate_empathetic_response(self, conversation_history: List[Dict[str, str]]) -> str:
        """
        Generate an empathetic response based on the recent conversation history.
        
        Args:
            conversation_history: List of conversation turns with 'role' and 'content' keys
        
        Returns:
            A short empathetic response (1-2 sentences)
        """
        # Extract the last 2-3 employee messages for context
        recent_messages = []
        for item in reversed(conversation_history):
            if item["role"] == "employee":
                recent_messages.append(f"Employee: {item['content']}")
                if len(recent_messages) >= 2:
                    break
        
        # Reverse to maintain chronological order
        recent_messages.reverse()
        
        # Create the prompt
        prompt = f"""
        Based on these recent messages from an employee during a counseling session:
        
        {' '.join(recent_messages)}
        
        First, use the following reasoning steps to determine if empathy is needed:
        
        Step 1: Identify the emotions present in the employee's last message. What feelings are they expressing?
        Step 2: Assess the intensity of these emotions. Are they expressing strong negative or vulnerable emotions?
        Step 3: Determine if the employee is sharing a personal challenge, difficulty, or vulnerability.
        Step 4: Consider if acknowledging these emotions would help the employee feel heard and understood.
        Step 5: Based on steps 1-4, decide if an empathetic response is needed (Yes/No).
        
        If your answer to Step 5 is "No", respond with ONLY the text "NO_EMPATHY_NEEDED".
        
        If your answer to Step 5 is "Yes", then:

        **IMPORTANT**: If empathy is really not needed, don't generate anything.

        Generate a very brief empathetic response (1 sentence) that acknowledges their feelings
        and creates a safe space. Your response should be warm and supportive, showing that you 
        understand what they're experiencing.
        
        Do NOT offer solutions or advice - just empathize with their situation and emotions.
        """
        
        # Use the agent to generate the response
        response = self.agent.run(prompt)
        
        # Extract just the text content and check if empathy is needed
        response_text = response.content.strip() if hasattr(
            response, "content") else str(response).strip()

        # Return empty string if empathy is not needed
        if response_text == "NO_EMPATHY_NEEDED":
            return ""

        return response_text

