from agno.agent import Agent
from agno.models.groq import Groq
import re
from prompt_templates import (
    COUNSELING_SYSTEM_PROMPT,
    QUESTION_GENERATION_PROMPT,
    NEXT_QUESTION_PROMPT,
    REPORT_GENERATION_PROMPT
)

class CounselingAgent:
    def __init__(self, model_id, api_key, kb_manager, system_prompt=None):
        """
        Initialize the counseling agent.
        
        Args:
            model_id: ID of the LLM to use (e.g., "llama-3.3-70b-versatile")
            api_key: API key for the model provider
            kb_manager: Knowledge base manager for retrieving relevant information
            system_prompt: Custom system prompt for the agent
        """
        self.system_prompt = system_prompt if system_prompt else COUNSELING_SYSTEM_PROMPT
        self.kb_manager = kb_manager
        
        # Initialize agent with a description
        self.agent = Agent(
            model=Groq(id=model_id, api_key=api_key),
            description=self.system_prompt,
            markdown=True,
        )
        
        self.conversation_history = []
        self.is_interview_complete = False
    
    def _get_response_text(self, run_response):
        """
        Extract the text from a RunResponse object, handling different response formats.
        
        Args:
            run_response: The RunResponse object from agent.run()
            
        Returns:
            The text response as a string
        """
        # Try different possible attributes that might contain the response
        if hasattr(run_response, 'content'):
            return run_response.content
        elif hasattr(run_response, 'message'):
            return run_response.message
        elif hasattr(run_response, 'response'):
            return run_response.response
        elif hasattr(run_response, 'text'):
            return run_response.text
        elif hasattr(run_response, 'output'):
            return run_response.output
        # If it's a string already, return it
        elif isinstance(run_response, str):
            return run_response
        # If all else fails, convert to string
        return str(run_response)
    
    def start_interview(self):
        """
        Start the counseling interview with an initial question
        generated based on retrieved information.
        """
        # Retrieve relevant information from both knowledge bases
        employee_data = self.kb_manager.retrieve_from_employee_data("employee profile summary", num_documents=1)
        question_templates = self.kb_manager.retrieve_from_questions("initial counseling questions", num_documents=1)
        
        # Create a prompt with the retrieved information
        prompt = QUESTION_GENERATION_PROMPT.format(
            employee_data=employee_data,
            question_templates=question_templates
        )
        
        # Generate the initial question
        response = self.agent.run(prompt)
        response_text = self._get_response_text(response)
        initial_question = self._extract_question(response_text)
        
        self.conversation_history.append({"role": "counselor", "content": initial_question})
        return initial_question
    
    def process_response(self, user_response):
        """
        Process the user's response and determine the next question to ask.
        
        Args:
            user_response: The user's response to the previous question
        
        Returns:
            The next question to ask, or an indication that the interview is complete
        """
        self.conversation_history.append({"role": "employee", "content": user_response})
        
        # Get the last 3 exchanges (or fewer if there aren't that many yet)
        recent_history = self.conversation_history[-min(6, len(self.conversation_history)):]
        
        # Create a condensed conversation history
        history_text = "\n".join([f"{'Counselor' if item['role'] == 'counselor' else 'Employee'}: {item['content']}" 
                                for item in recent_history])
        
        # Create a search query based on the conversation
        search_query = f"Counseling questions related to: {user_response}"
        
        # Retrieve relevant information based on the conversation
        employee_data = self.kb_manager.retrieve_from_employee_data(search_query, num_documents=1)
        question_templates = self.kb_manager.retrieve_from_questions(search_query, num_documents=1)
        
        # Check if we've had enough exchanges to complete the interview (minimum 5 questions)
        counselor_turns = sum(1 for item in self.conversation_history if item["role"] == "counselor")
        
        # Create the prompt for the next question
        prompt = NEXT_QUESTION_PROMPT.format(
            conversation_history=history_text,
            employee_data=employee_data,
            question_templates=question_templates,
            enough_turns=(counselor_turns >= 5)
        )
        
        # Generate the next question or completion message
        response = self.agent.run(prompt)
        response_text = self._get_response_text(response)
        
        if response_text.startswith("COMPLETE:"):
            self.is_interview_complete = True
            return None
        elif response_text.startswith("CONTINUE:"):
            next_question = response_text.replace("CONTINUE:", "").strip()
            self.conversation_history.append({"role": "counselor", "content": next_question})
            return next_question
        else:
            # If the model doesn't follow the format, extract the likely question
            next_question = self._extract_question(response_text)
            self.conversation_history.append({"role": "counselor", "content": next_question})
            return next_question
    
    def _extract_question(self, text):
        """Extract the question from the model response"""
        # Simple heuristic: look for sentence ending with question mark
        sentences = re.split(r'(?<=[.!?])\s+', text)
        for sentence in sentences:
            if '?' in sentence:
                return sentence.strip()
        
        # If no question mark found, return the entire text
        return text.strip()
    
    def generate_report(self):
        """
        Generate a comprehensive report based on the conversation history and employee data.
        
        Returns:
            A detailed report on the employee
        """
        # Create a condensed conversation history
        history_text = "\n".join([f"{'Counselor' if item['role'] == 'counselor' else 'Employee'}: {item['content']}" 
                                for item in self.conversation_history])
        
        # Retrieve key employee information for the report
        employee_data = self.kb_manager.retrieve_from_employee_data("employee performance summary leaves activity", num_documents=2)
        
        # Create the prompt for the report generation
        prompt = REPORT_GENERATION_PROMPT.format(
            conversation_history=history_text[:1500],  # Limit the history to 1500 characters 
            employee_data=employee_data
        )
        
        # Generate the report
        response = self.agent.run(prompt)
        return self._get_response_text(response)