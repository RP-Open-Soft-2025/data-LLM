from typing import Dict, Any, List
from langchain_groq import ChatGroq
import random
from datetime import datetime

from vector_store import VectorStore
from conversation_tracker import ConversationTracker
from prompt_templates import (
    initial_question_prompt,
    contextual_question_prompt,
    behavioral_report_prompt,
    PREDEFINED_INITIAL_QUESTIONS
)
from utils import format_conversation_for_prompt

class CounselingAgent:
    def __init__(self, vector_store: VectorStore, conversation_tracker: ConversationTracker, 
                 groq_api_key: str, max_questions: int = 5):
        """Initialize the counseling agent with components and configuration."""
        self.vector_store = vector_store
        self.conversation_tracker = conversation_tracker
        self.max_questions = max_questions
        self.question_count = 0
        self.used_questions = set()  # Track used questions to avoid repetition
        
        # Current user and datetime info
        self.current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.current_user = "bibhabasuiitkgp"  # Or get this dynamically
        
        # Initialize Groq LLM
        self.llm = ChatGroq(
            api_key=groq_api_key,
            model_name="llama3-70b-8192",
            temperature=0.7,
            max_tokens=1024
        )
    
    def generate_initial_question(self) -> str:
        """Generate or select an initial question."""
        # First, try to use a predefined question
        if PREDEFINED_INITIAL_QUESTIONS:
            # Filter out any questions we've used before
            unused_questions = [q for q in PREDEFINED_INITIAL_QUESTIONS if q not in self.used_questions]
            
            # If we have unused questions, use one of them
            if unused_questions:
                question = random.choice(unused_questions)
                self.used_questions.add(question)
                return question
        
        # If we've used all predefined questions or there are none, generate a new one
        try:
            # Get random query terms to ensure diversity
            query_terms = [
                "employee performance goals achievements",
                "workplace challenges opportunities growth",
                "professional development skills improvement",
                "team collaboration leadership experience",
                "work environment satisfaction motivation"
            ]
            
            query = random.choice(query_terms)
            
            # Get context with some randomness in the retrieval
            employee_context = self.vector_store.get_employee_context(query, k=random.randint(2, 4))
            behavioral_context = self.vector_store.get_behavioral_context(query, k=random.randint(2, 4))
            
            # Add some dynamic elements to ensure question diversity
            prompt = initial_question_prompt.format(
                employee_context=employee_context,
                behavioral_context=behavioral_context
            )
            
            # Add a prompt suffix to encourage diversity
            prompt += f"\nMake sure to create a unique question different from common questions. Today is {self.current_datetime} and this question is for user {self.current_user}."
            
            # Increase temperature for more creativity
            self.llm.temperature = 0.9
            question = self.llm.invoke(prompt).content
            self.llm.temperature = 0.7  # Reset temperature
            
            # Store the question to avoid repetition
            self.used_questions.add(question)
            return question
        except Exception as e:
            print(f"Warning: Failed to generate initial question: {e}")
            # Fallback to a random predefined question or create a simple one
            fallback_questions = [
                "Tell me about a challenging situation you've faced in your career.",
                "What would you say are your greatest strengths in a professional setting?",
                "How do you typically approach conflict with colleagues?",
                "What motivates you most in your work environment?",
                "How do you handle feedback and criticism?"
            ]
            return random.choice(fallback_questions)
    
    def generate_follow_up_question(self) -> str:
        """Generate a follow-up question based on conversation context."""
        try:
            # Get the most recent context
            conversation_context = self.conversation_tracker.get_context()
            
            # Add a random element to the query to ensure diversity
            diversifiers = [
                "next steps", "deeper insight", "alternative perspective", 
                "specific examples", "emotional response", "lessons learned",
                "future application", "related experiences"
            ]
            random_element = random.choice(diversifiers)
            
            # Create a more diverse query
            query = f"{conversation_context} {random_element}" if conversation_context else "employee skills behavior assessment"
            contexts = self.vector_store.get_relevant_context(query, k=random.randint(2, 4))
            
            # Generate the question
            prompt = contextual_question_prompt.format(
                employee_context=contexts["employee_context"],
                behavioral_context=contexts["behavioral_context"],
                conversation_context=conversation_context
            )
            
            # Add a prompt suffix to ensure the question is different from previous ones
            prompt += f"\nMake sure this question is COMPLETELY DIFFERENT from any previous questions. Explore a new angle or topic. Do not repeat similar themes. Current date: {self.current_datetime}."
            
            # Temporary increase in temperature for more diversity
            self.llm.temperature = 0.8
            question = self.llm.invoke(prompt).content
            self.llm.temperature = 0.7  # Reset temperature
            
            return question
        except Exception as e:
            print(f"Warning: Failed to generate follow-up question: {e}")
            # Fallback to a generic follow-up question
            fallback_questions = [
                "Could you elaborate more on your previous answer?",
                "That's interesting. Can you share a specific example related to this?",
                "How did that experience affect your approach to similar situations?",
                "What lessons did you learn from that situation?",
                "How might you handle a similar situation differently in the future?"
            ]
            return random.choice(fallback_questions)
    
    def generate_behavioral_report(self) -> str:
        """Generate a behavioral report based on the full conversation."""
        try:
            # Get a summarized version of the conversation
            conversation_history = self.conversation_tracker.get_conversation_history()
            conversation_summary = format_conversation_for_prompt(conversation_history)
            
            # Get relevant contexts for the report
            contexts = self.vector_store.get_relevant_context("employee evaluation performance assessment")
            
            # Generate the report
            prompt = behavioral_report_prompt.format(
                employee_context=contexts["employee_context"],
                behavioral_context=contexts["behavioral_context"],
                conversation_summary=conversation_summary
            )
            
            report = self.llm.invoke(prompt).content
            return report
        except Exception as e:
            print(f"Warning: Failed to generate report: {e}")
            return "Unable to generate a complete report due to technical issues. Please try again later."
    
    def run_session(self) -> Dict[str, Any]:
        """Run a complete counseling session."""
        # Generate and display initial question
        initial_question = self.generate_initial_question()
        self.conversation_tracker.add_message("bot", initial_question)
        print(f"\nCounselor: {initial_question}")
        
        # Main interaction loop
        for i in range(self.max_questions):
            # Get user input
            user_answer = input("\nYou: ")
            self.conversation_tracker.add_message("user", user_answer)
            
            # Check for session termination request
            if "end session" in user_answer.lower() or "finish session" in user_answer.lower():
                print("\nEnding session early at user request.")
                break
            
            # Update the context
            self.conversation_tracker.update_context()
            
            # Generate next question (if not the last round)
            if i < self.max_questions - 1:
                next_question = self.generate_follow_up_question()
                self.conversation_tracker.add_message("bot", next_question)
                print(f"\nCounselor: {next_question}")
        
        # Generate the final report
        print("\nGenerating behavioral report...")
        report = self.generate_behavioral_report()
        
        return {"report": report}