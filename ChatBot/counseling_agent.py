from agno.agent import Agent
from agno.models.groq import Groq
import re
from agno.models.openai import OpenAIChat
from agno.tools.thinking import ThinkingTools
from .prompt_templates import (
    COUNSELING_SYSTEM_PROMPT,
    QUESTION_GENERATION_PROMPT,
    NEXT_QUESTION_PROMPT,  # Added NEXT_QUESTION_PROMPT to import list
    SUGGESTION_GENERATION_PROMPT,
    FOLLOW_UP_PROMPT,
    NEW_SUGGESTION_PROMPT,
    REPORT_GENERATION_PROMPT
)
from dotenv import load_dotenv
import os
load_dotenv()

class CounselingAgent:
    def __init__(self, model_id, kb_manager, system_prompt=None):
        """
        Initialize the counseling agent.
        
        Args:
            model_id: ID of the LLM to use (e.g., "llama-3.3-70b-versatile")
            kb_manager: Knowledge base manager for retrieving relevant information
            system_prompt: Custom system prompt for the agent
        """
        self.system_prompt = system_prompt if system_prompt else COUNSELING_SYSTEM_PROMPT
        self.kb_manager = kb_manager
        
        os.getenv("OPENAI_API_KEY")
        self.agent = Agent(
            model=OpenAIChat(id="gpt-4o-mini"),
            tools=[ThinkingTools()],
            markdown=True,
            description=self.system_prompt
        )
        
        self.conversation_history = []
        self.question_count = 0
        self.initial_questions = []
        self.suggestions = []
        self.previous_suggestions = []
        self.accepted_suggestions = []
        self.is_interview_complete = False
        
        # Store prompt templates
        self.question_prompt = QUESTION_GENERATION_PROMPT
        self.next_question_prompt = NEXT_QUESTION_PROMPT
        self.suggestion_prompt = SUGGESTION_GENERATION_PROMPT
        self.follow_up_prompt = FOLLOW_UP_PROMPT
        self.new_suggestion_prompt = NEW_SUGGESTION_PROMPT
        self.report_prompt = REPORT_GENERATION_PROMPT
    
    def set_question_prompt(self, prompt):
        """Set the question generation prompt template"""
        self.question_prompt = prompt
    
    def set_next_question_prompt(self, prompt):
        """Set the next question generation prompt template"""
        self.next_question_prompt = prompt
    
    def set_suggestion_prompt(self, prompt):
        """Set the suggestion generation prompt template"""
        self.suggestion_prompt = prompt
    
    def set_follow_up_prompt(self, prompt):
        """Set the follow-up question prompt template"""
        self.follow_up_prompt = prompt
    
    def set_new_suggestion_prompt(self, prompt):
        """Set the new suggestion generation prompt template"""
        self.new_suggestion_prompt = prompt
    
    def set_report_prompt(self, prompt):
        """Set the report generation prompt template"""
        self.report_prompt = prompt
    
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
        elif isinstance(run_response, str):
            return run_response
        return str(run_response)
    
    def generate_initial_questions(self):
        """
        Generate a set of 7 initial personalized questions based on employee data.
        
        Returns:
            List of 7 questions
        """
        # Retrieve relevant information from both knowledge bases
        employee_data = self.kb_manager.retrieve_from_employee_data("employee profile summary", num_documents=3)
        
        # Create a prompt with the retrieved information
        prompt = self.question_prompt.format(
            employee_data=employee_data
        )
        
        # Generate the initial questions
        response = self.agent.run(prompt)
        response_text = self._get_response_text(response)
        
        # Extract the 7 questions
        questions = []
        lines = response_text.strip().split('\n')
        for line in lines:
            if line.startswith("Question") and ":" in line:
                question = line.split(":", 1)[1].strip()
                questions.append(question)
        
        # If we don't get exactly 7 questions, we need to generate more personalized ones
        if len(questions) < 7:
            # Use the next_question_prompt to generate additional questions
            while len(questions) < 7:
                # Create a conversation history from existing questions and responses
                # Handle case where there's no conversation history yet
                history_text = self._format_conversation_history() if self.conversation_history else "No conversation history yet."
                
                # List previous questions to avoid repetition
                previous_questions = "\n".join([f"- {q}" for q in questions])
                
                # Generate a new personalized question
                prompt = self.next_question_prompt.format(
                    employee_data=employee_data,
                    conversation_history=history_text,
                    previous_questions=previous_questions
                )
                
                response = self.agent.run(prompt)
                new_question = self._get_response_text(response)
                
                # Clean up the question
                new_question = self._extract_question(new_question)
                
                if new_question and new_question not in questions:
                    questions.append(new_question)
        
        self.initial_questions = questions[:7]
        
        # Add initial questions to conversation history
        for question in self.initial_questions:
            self.conversation_history.append({"role": "counselor", "content": question})
            
        return "I'd like to ask you 7 questions to help me better understand your situation so I can provide the most helpful support."
    
    def get_next_question(self):
        """
        Get the next question in the sequence, ensuring it's personalized based on context.
        
        Returns:
            The next personalized question to ask
        """
        if self.question_count < len(self.initial_questions):
            # Return the next pre-generated question
            question = self.initial_questions[self.question_count]
            return question
        else:
            # This shouldn't be reached in the normal flow, but handle it anyway
            # Generate a new personalized question based on the conversation history
            employee_data = self.kb_manager.retrieve_from_employee_data("employee profile summary", num_documents=3)
            history_text = self._format_conversation_history()
            previous_questions = "\n".join([
                f"- {item['content']}" for item in self.conversation_history 
                if item['role'] == 'counselor' and '?' in item['content']
            ])
            
            prompt = self.next_question_prompt.format(
                employee_data=employee_data,
                conversation_history=history_text,
                previous_questions=previous_questions
            )
            
            response = self.agent.run(prompt)
            new_question = self._get_response_text(response)
            new_question = self._extract_question(new_question)
            
            # Add to conversation history
            self.conversation_history.append({"role": "counselor", "content": new_question})
            
            return new_question
    
    def _format_conversation_history(self):
        """Format the conversation history for use in prompts"""
        return "\n".join([
            f"{'Counselor' if item['role'] == 'counselor' else 'Employee'}: {item['content']}" 
            for item in self.conversation_history
        ])
    
    def record_response(self, question_number, response):
        """
        Record the employee's response to a question.
        
        Args:
            question_number: The number of the question (1-7)
            response: The employee's response
        """
        self.conversation_history.append({"role": "employee", "content": response})
        self.question_count += 1
    
    def is_satisfied_with_suggestions(self, response):
        """
        Determine if the employee is satisfied with the suggestions and which ones they accepted.
        
        Args:
            response: The employee's response about the suggestions
            
        Returns:
            Tuple of (is_satisfied, accepted_indices)
        """
        # Add to conversation history
        self.conversation_history.append({"role": "employee", "content": response})
        
        # Extract accepted suggestion indices
        accepted_indices = self.extract_accepted_suggestions(response)
        
        # Determine if they are satisfied
        # They are satisfied if they accepted at least one suggestion
        is_satisfied = len(accepted_indices) > 0
        
        # If satisfied, update the accepted suggestions
        if is_satisfied:
            self.set_accepted_suggestions(accepted_indices)
            
        return is_satisfied, accepted_indices
    
    def generate_suggestions(self):
        """
        Generate 3 personalized suggestions based on the employee's responses.
        
        Returns:
            List of 3 suggestions
        """
        # Create a condensed conversation history
        history_text = self._format_conversation_history()
        
        # Retrieve employee data
        employee_data = self.kb_manager.retrieve_from_employee_data("employee profile summary", num_documents=3)
        
        # Create the prompt for suggestion generation
        prompt = self.suggestion_prompt.format(
            conversation_history=history_text,
            employee_data=employee_data
        )
        
        # Generate suggestions
        response = self.agent.run(prompt)
        response_text = self._get_response_text(response)        
        # Extract the suggestions
        suggestions = []
        lines = response_text.strip().split('\n')
        for line in lines:
            if line.startswith("Suggestion") and ":" in line:
                suggestion = line.split(":", 1)[1].strip()
                suggestions.append(suggestion)
        
        # If we don't get exactly 3 suggestions, generate more using the conversation context
        while len(suggestions) < 3:
            prompt = f"Based on this conversation:\n{history_text}\n\nGenerate ONE more specific, actionable, and personalized suggestion (max 175 characters) for this employee."
            response = self.agent.run(prompt)
            new_suggestion = self._get_response_text(response)
            
            # Clean up and extract just the suggestion
            new_suggestion = new_suggestion.replace("Suggestion:", "").strip()
            if len(new_suggestion) > 175:
                new_suggestion = new_suggestion[:172] + "..."
                
            if new_suggestion and new_suggestion not in suggestions:
                suggestions.append(new_suggestion)
        
        self.suggestions = suggestions[:3]
        return self.suggestions
    
    def extract_accepted_suggestions(self, response):
        """
        Extract which suggestions the employee has accepted from their response.
        
        Args:
            response: The employee's response about suggestion satisfaction
            
        Returns:
            List of accepted suggestion indices
        """
        accepted = []
        
        # Check for numbers in the response
        numbers = re.findall(r'\b[1-3]\b', response)
        for num in numbers:
            index = int(num) - 1
            if 0 <= index < len(self.suggestions):
                accepted.append(index)
        
        # If no numbers found, check for other indicators
        if not accepted:
            response_lower = response.lower()
            if "first" in response_lower or "1st" in response_lower:
                accepted.append(0)
            if "second" in response_lower or "2nd" in response_lower:
                accepted.append(1)
            if "third" in response_lower or "3rd" in response_lower:
                accepted.append(2)
            if "all" in response_lower or "every" in response_lower or "all of them" in response_lower:
                accepted = [0, 1, 2]
        
        return accepted
    
    def set_accepted_suggestions(self, indices):
        """
        Set which suggestions were accepted by the employee.
        
        Args:
            indices: List of suggestion indices that were accepted
        """
        self.accepted_suggestions = [self.suggestions[i] for i in indices if 0 <= i < len(self.suggestions)]
        if self.accepted_suggestions:
            self.is_interview_complete = True
    
    def generate_follow_up_questions(self, add_to_history=True):
        """
        Generate 2 personalized follow-up questions when the employee is not satisfied with suggestions.
        
        Args:
            add_to_history: Whether to add the questions to conversation history
        
        Returns:
            List of 2 follow-up questions
        """
        # Save the rejected suggestions before generating new ones
        self.previous_suggestions = self.suggestions.copy()
        
        # Create a condensed conversation history
        history_text = self._format_conversation_history()
        
        # Format previous suggestions
        previous_suggestions_text = "\n".join([f"- {suggestion}" for suggestion in self.previous_suggestions])
        
        # Retrieve employee data
        employee_data = self.kb_manager.retrieve_from_employee_data("employee profile summary", num_documents=3)
        
        # Get previous questions from conversation history
        previous_questions = "\n".join([
            f"- {item['content']}" for item in self.conversation_history 
            if item['role'] == 'counselor' and '?' in item['content']
        ])
        
        # Create the prompt for follow-up questions
        prompt = self.follow_up_prompt.format(
            conversation_history=history_text,
            employee_data=employee_data,
            previous_suggestions=previous_suggestions_text,
            previous_questions=previous_questions  # Add the missing parameter
        )
        
        # Generate follow-up questions
        response = self.agent.run(prompt)
        response_text = self._get_response_text(response)
        
        # Extract the questions
        questions = []
        lines = response_text.strip().split('\n')
        for line in lines:
            # Look for lines with question marks or that start with "Question"
            if "?" in line:
                # Clean up any numbering or prefixes
                question = re.sub(r'^(Question \d+:|Q\d+:|Follow-up \d+:|Follow-up question \d+:|\d+\.|\*)\s*', '', line).strip()
                if question and question not in questions:
                    questions.append(question)
        
        # If we don't get exactly 2 questions, generate more using the conversation context
        while len(questions) < 2:
            # Generate a highly personalized follow-up question
            prompt = f"""Based on this conversation:
{history_text}

And these previously rejected suggestions:
{previous_suggestions_text}

Generate ONE personalized follow-up question (max 175 chars) to better understand what the employee needs. The question should:
1. Address why they might not have liked the suggestions
2. Explore a new aspect of their situation
3. Show active listening by referencing points they've made
4. Be empathetic and open-ended
5. NOT be generic
"""
            response = self.agent.run(prompt)
            new_question = self._get_response_text(response)
            
            # Clean up and extract just the question
            new_question = self._extract_question(new_question)
                
            if new_question and new_question not in questions:
                questions.append(new_question)
        
        follow_up_questions = questions[:2]
        
        # Add the follow-up questions to the conversation history if specified
        if add_to_history:
            for question in follow_up_questions:
                self.conversation_history.append({"role": "counselor", "content": question})
        
        return follow_up_questions
    
    def record_follow_up_response(self, question, response):
        """
        Record the employee's response to a follow-up question.
        
        Args:
            question: The follow-up question
            response: The employee's response
        """
        self.conversation_history.append({"role": "employee", "content": response})
    
    def generate_new_suggestions(self):
        """
        Generate 3 new personalized suggestions based on follow-up responses.
        
        Returns:
            List of 3 new suggestions
        """
        # Create a condensed conversation history
        history_text = self._format_conversation_history()
        
        # Format previous suggestions
        previous_suggestions_text = "\n".join([f"- {suggestion}" for suggestion in self.previous_suggestions])
        
        # Retrieve employee data
        employee_data = self.kb_manager.retrieve_from_employee_data("employee profile summary", num_documents=3)
        
        # Create the prompt for new suggestions
        prompt = self.new_suggestion_prompt.format(
            conversation_history=history_text,
            employee_data=employee_data,
            previous_suggestions=previous_suggestions_text
        )
        
        # Generate new suggestions
        response = self.agent.run(prompt)
        response_text = self._get_response_text(response)
        
        # Extract the suggestions
        new_suggestions = []
        lines = response_text.strip().split('\n')
        for line in lines:
            if ("New Suggestion" in line or "Suggestion" in line) and ":" in line:
                suggestion = line.split(":", 1)[1].strip()
                new_suggestions.append(suggestion)
        
        # If we don't get exactly 3 suggestions, generate more using the conversation context
        while len(new_suggestions) < 3:
            prompt = f"""Based on this conversation:
{history_text}

And these previously rejected suggestions:
{previous_suggestions_text}

Generate ONE new, specific, and personalized suggestion (max 175 chars) that:
1. Is different from the rejected suggestions
2. Addresses the most recent feedback
3. Is actionable and practical
4. Shows understanding of their unique situation
"""
            response = self.agent.run(prompt)
            new_suggestion = self._get_response_text(response)
            
            # Clean up and extract just the suggestion
            new_suggestion = new_suggestion.replace("New Suggestion:", "").replace("Suggestion:", "").strip()
            if len(new_suggestion) > 175:
                new_suggestion = new_suggestion[:172] + "..."
                
            if new_suggestion and new_suggestion not in new_suggestions and new_suggestion not in self.previous_suggestions:
                new_suggestions.append(new_suggestion)
        
        self.suggestions = new_suggestions[:3]
        return self.suggestions
    
    def _extract_question(self, text):
        """Extract a clean question from the model response"""
        # Look for sentences with question marks
        sentences = re.split(r'(?<=[.!?])\s+', text)
        for sentence in sentences:
            if '?' in sentence:
                question = sentence.strip()
                # Remove any numbering or prefixes
                question = re.sub(r'^(Question \d+:|Q\d+:|Follow-up \d+:|Follow-up question \d+:|\d+\.|\*)\s*', '', question).strip()
                return question
        
        # If no question mark found, return the whole text, cleaned up
        cleaned_text = re.sub(r'^(Question:|Follow-up:|Here\'s a question:|I would ask:)\s*', '', text.strip())
        if len(cleaned_text) > 175:
            cleaned_text = cleaned_text[:172] + "..."
        return cleaned_text
    
    def generate_report(self):
        """
        Generate a comprehensive report based on the conversation history, employee data, and accepted suggestions.
        
        Returns:
            A detailed report on the employee
        """
        # Create a condensed conversation history
        history_text = self._format_conversation_history()
        
        # Retrieve key employee information for the report
        employee_data = self.kb_manager.retrieve_from_employee_data("employee performance summary leaves activity", num_documents=3)
        
        # Create a string of accepted suggestions
        accepted_suggestions_text = "\n".join([f"- {suggestion}" for suggestion in self.accepted_suggestions])
        
        # Create the prompt for the report generation
        prompt = self.report_prompt.format(
            conversation_history=history_text[:1500],  # Limit the history to 1500 characters
            employee_data=employee_data,
            accepted_suggestions=accepted_suggestions_text
        )
        
        # Generate the report
        response = self.agent.run(prompt)
        return self._get_response_text(response)