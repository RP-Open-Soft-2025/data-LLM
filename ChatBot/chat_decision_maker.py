from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.tools.thinking import ThinkingTools
from .prompt_templates import DECISION_MAKER_DESCRIPTION, DECISION_MAKER_INSTRUCTIONS, DECISION_MAKER_QUERY
import os

class ChatDecisionMaker:
    def __init__(self, model_id=None):
        """
        Initialize the chat decision maker agent.
        
        Args:
            model_id: ID of the OpenAI model to use
        """
        api_key = os.getenv("OPENAI_API_KEY")
        model = OpenAIChat(id=model_id, api_key=api_key) if model_id else OpenAIChat(api_key=api_key)
        
        self.agent = Agent(
            model=model,
            description=DECISION_MAKER_DESCRIPTION,
            instructions=DECISION_MAKER_INSTRUCTIONS,
            tools=[ThinkingTools()],
            markdown=True,
        )
    
    def make_decision(self, conversation_history, employee_data, context=None):
        """
        Analyze the conversation and make decisions on:
        1. Whether to change the topic
        2. Whether to escalate to HR
        3. Whether to end the chat
        
        Args:
            conversation_history: List of conversation exchanges
            employee_data: Employee information
            context: Previous conversation context (if any)
            
        Returns:
            Tuple of (change_topic, escalate_to_hr, end_chat) as boolean values
        """
        # Format conversation history
        history_text = "\n".join(
            [
                f"{'Counselor' if item['role'] == 'counselor' else 'Employee'}: {item['content']}"
                for item in conversation_history
            ]
        )
        
        # Create query for decision making
        query = DECISION_MAKER_QUERY.format(
            conversation_history=history_text,
            employee_data=employee_data,
            context=context if context else ""
        )
        
        # Get decision from the agent
        response = self.agent.run(query)
        response_text = response.content if hasattr(response, "content") else str(response)
        
        # Parse the response to extract decisions
        decisions = self._parse_decision(response_text)
        return decisions
    
    def _parse_decision(self, decision_text):
        """
        Parse the decision text and extract boolean values.
        Expected format: "DECISION: change_topic=True/False, escalate_to_hr=True/False, end_chat=True/False"
        
        Args:
            decision_text: The raw text response from the agent
            
        Returns:
            Tuple of (change_topic, escalate_to_hr, end_chat) as boolean values
        """
        # Default values
        change_topic = False
        escalate_to_hr = False
        end_chat = False
        
        # Extract the decision part
        if "DECISION:" in decision_text:
            decision_part = decision_text.split("DECISION:")[1].strip()
            
            # Parse each decision
            if "change_topic=" in decision_part:
                change_topic = "change_topic=True" in decision_part
            
            if "escalate_to_hr=" in decision_part:
                escalate_to_hr = "escalate_to_hr=True" in decision_part
            
            if "end_chat=" in decision_part:
                end_chat = "end_chat=True" in decision_part
        
        return (change_topic, escalate_to_hr, end_chat)
