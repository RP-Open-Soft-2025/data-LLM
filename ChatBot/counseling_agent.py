from agno.agent import Agent
from agno.models.groq import Groq
import re
from agno.models.google import Gemini
from agno.models.openai import OpenAIChat
from agno.tools.thinking import ThinkingTools
from .prompt_templates import (
    COUNSELING_SYSTEM_PROMPT,
    INITIAL_QUESTION_DESCRIPTION,
    CONTEXT_QUESTION_DESCRIPTION,
    NEXT_QUESTION_DESCRIPTION,
    REPORT_GENERATION_DESCRIPTION,
    INITIAL_QUESTION_INSTRUCTIONS,
    CONTEXT_QUESTION_INSTRUCTIONS,
    NEXT_QUESTION_INSTRUCTIONS,
    REPORT_GENERATION_INSTRUCTIONS,
    INITIAL_QUESTION_QUERY,
    CONTEXT_QUESTION_QUERY,
    NEXT_QUESTION_QUERY,
    REPORT_GENERATION_QUERY,
    CONTINUE_TOPIC_PROMPT,
    CHANGE_TOPIC_PROMPT,
    END_CHAT_PROMPT,
    ESCALATION_PROMPT,
)
from dotenv import load_dotenv
import os
from . import config
from .empathizer_agent import EmpathizerAgent
from .chat_decision_maker import ChatDecisionMaker

load_dotenv()


class CounselingAgent:
    def __init__(
        self,
        model_id,
        kb_manager,
        system_prompt=None,
        context=None,
        report_file_path=None,
    ):
        """
        Initialize the counseling agent.

        Args:
            model_id: ID of the LLM to use
            kb_manager: Knowledge base manager for retrieving relevant information
            system_prompt: Custom system prompt for the agent
            context: Previous conversation context/summary (if any)
        """
        self.system_prompt = (
            system_prompt if system_prompt else COUNSELING_SYSTEM_PROMPT
        )
        self.kb_manager = kb_manager
        self.context = context if context else ""

        # Set up the model
        api_key = os.getenv("OPENAI_API_KEY")
        print("API KEY: ", api_key)
        model = OpenAIChat(id=model_id, api_key=api_key)

        # Initialize specialized agents for different tasks
        self.initial_agent = Agent(
            model=model,
            description=INITIAL_QUESTION_DESCRIPTION,
            instructions=INITIAL_QUESTION_INSTRUCTIONS,
            tools=[ThinkingTools()],
            markdown=True,
        )

        self.context_agent = Agent(
            model=model,
            description=CONTEXT_QUESTION_DESCRIPTION,
            instructions=CONTEXT_QUESTION_INSTRUCTIONS,
            tools=[ThinkingTools()],
            markdown=True,
        )

        self.next_question_agent = Agent(
            model=model,
            description=NEXT_QUESTION_DESCRIPTION,
            instructions=NEXT_QUESTION_INSTRUCTIONS,
            tools=[ThinkingTools()],
            markdown=True,
        )

        self.report_agent = Agent(
            model=model,
            description=REPORT_GENERATION_DESCRIPTION,
            instructions=REPORT_GENERATION_INSTRUCTIONS,
            tools=[ThinkingTools()],
            markdown=True,
        )

        # Initialize specialized agents for specific conversation tasks
        self.continue_topic_agent = Agent(
            model=model,
            description="Expert at exploring topics deeply in counseling conversations",
            instructions=[
                "Create follow-up questions that deepen understanding while showing empathy"],
            tools=[ThinkingTools()],
            markdown=True,
        )

        self.change_topic_agent = Agent(
            model=model,
            description="Expert at smoothly transitioning between topics in counseling",
            instructions=[
                "Create transition questions that acknowledge previous topics while introducing new ones"],
            tools=[ThinkingTools()],
            markdown=True,
        )

        self.end_chat_agent = Agent(
            model=model,
            description="Expert at closing counseling conversations meaningfully",
            instructions=[
                "Create closing messages that summarize, acknowledge progress, and offer support"],
            tools=[ThinkingTools()],
            markdown=True,
        )

        self.escalation_agent = Agent(
            model=model,
            description="Expert at handling sensitive HR escalations",
            instructions=[
                "Create messages that show concern while explaining the need for additional support"],
            tools=[ThinkingTools()],
            markdown=True,
        )

        # Initialize the empathizer agent with a lightweight model
        self.empathizer_agent = EmpathizerAgent()

        # Initialize the decision maker agent
        self.decision_maker = ChatDecisionMaker(model_id)

        # Prepare employee data
        if report_file_path:
            with open(report_file_path, "r") as file:
                self.employee_data = file.read()
        else:
            with open(config.EMPLOYEE_DATA_PATH, "r") as file:
                self.employee_data = file.read()

        # Retrieve relevant question templates
        search_query = f"""
        Summary of chat history of an employee's counselling sessions (note that this can be empty):
        {context}

        Please find questions that are not covered with reference to the above context
        """
        self.question_templates = self.kb_manager.retrieve_from_questions(
            search_query, num_documents=1
        )

        self.current_topic = None
        self.explored_topics = set()
        self.remaining_topics = set()
        self.conversation_history = []
        self.is_interview_complete = False
        self.is_escalated_to_hr = False

    def _get_response_text(self, run_response):
        """
        Extract the text from a RunResponse object, handling different response formats.

        Args:
            run_response: The RunResponse object from agent.run()

        Returns:
            The text response as a string
        """
        # Try different possible attributes that might contain the response
        if hasattr(run_response, "content"):
            return run_response.content
        elif hasattr(run_response, "message"):
            return run_response.message
        elif hasattr(run_response, "response"):
            return run_response.response
        elif hasattr(run_response, "text"):
            return run_response.text
        elif hasattr(run_response, "output"):
            return run_response.output
        # If it's a string already, return it
        elif isinstance(run_response, str):
            return run_response
        # If all else fails, convert to string
        return str(run_response)

    def start_interview(self):
        """
        Start the counseling interview with an initial question
        generated based on retrieved information and context (if available).
        """
        # Retrieve relevant information from both knowledge bases
        employee_data = self.kb_manager.retrieve_from_employee_data(
            "Please extract all the issues from the text", num_documents=1
        )
        question_templates = self.kb_manager.retrieve_from_questions(
            "initial counseling questions", num_documents=1
        )

        # Use appropriate agent based on context availability
        if self.context:
            # Use context-aware agent
            query = CONTEXT_QUESTION_QUERY.format(
                employee_data=employee_data,
                question_templates=question_templates,
                context=self.context,
            )
            response = self.context_agent.run(query)
        else:
            # Use standard initial question agent
            query = INITIAL_QUESTION_QUERY.format(
                employee_data=employee_data,
                question_templates=question_templates,
            )
            response = self.initial_agent.run(query)

        response_text = self._get_response_text(response)
        initial_question = self._extract_question(response_text)

        self.conversation_history.append(
            {"role": "counselor", "content": initial_question}
        )
        return initial_question

    def process_response(self, user_response):
        """
        Process the user's response and determine the next question to ask.

        Args:
            user_response: The user's response to the previous question

        Returns:
            The next question to ask, or an indication that the interview is complete
            or has been escalated to HR
        """
        self.conversation_history.append({"role": "employee", "content": user_response})

        # Create a condensed conversation history
        history_text = "\n".join(
            [
                f"{'Counselor' if item['role'] == 'counselor' else 'Employee'}: {item['content']}"
                for item in self.conversation_history
            ]
        )

        # Generate empathetic response using the empathizer agent
        empathetic_response = self.empathizer_agent.generate_empathetic_response(
            self.conversation_history
        )

        # Use the decision maker to determine next steps
        change_topic, escalate_to_hr, end_chat = self.decision_maker.make_decision(
            self.conversation_history,
            self.employee_data,
            self.context
        )

        # Handle decisions based on the decision maker's output
        if escalate_to_hr:
            self.is_interview_complete = True
            self.is_escalated_to_hr = True

            # Generate escalation message with properly formatted prompt
            escalation_query = ESCALATION_PROMPT.format(
                conversation_history=history_text,
                employee_data=self.employee_data,
                context=self.context
            )
            response = self.escalation_agent.run(escalation_query)
            response_text = self._get_response_text(response)

            self.conversation_history.append(
                {"role": "counselor", "content": response_text}
            )
            return f"{response_text}"

        elif end_chat:
            self.is_interview_complete = True

            # Generate closing message with properly formatted prompt including empathetic_response
            end_chat_query = END_CHAT_PROMPT.format(
                conversation_history=history_text,
                employee_data=self.employee_data,
                context=self.context,
                # empathetic_response=empathetic_response
            )
            response = self.end_chat_agent.run(end_chat_query)
            response_text = self._get_response_text(response)

            self.conversation_history.append(
                {"role": "counselor", "content": response_text}
            )
            return f"{empathetic_response} {response_text}"

        elif change_topic:
            # Extract current and potential next topics from employee data
            if not self.current_topic:
                self.current_topic = "general well-being"  # Default initial topic

            # Update the change_topic_agent instructions to use NEXT_QUESTION_INSTRUCTIONS
            self.change_topic_agent.instructions = NEXT_QUESTION_INSTRUCTIONS

            # Generate a question that changes the topic with properly formatted prompt including empathetic_response
            change_topic_query = CHANGE_TOPIC_PROMPT.format(
                conversation_history=history_text,
                employee_data=self.employee_data,
                context=self.context,
                question_templates=self.question_templates,
                previous_topic=self.current_topic,
                next_topic="another aspect of your experience",
                empathetic_response=empathetic_response
            )

            response = self.change_topic_agent.run(change_topic_query)
            response_text = self._get_response_text(response)
            next_question = self._extract_question(response_text)

            # Update current topic - in practice, you'd extract this from the new question
            self.explored_topics.add(self.current_topic)
            self.current_topic = "new topic"  # This would be more specific in practice

        else:
            # Update the continue_topic_agent instructions to use NEXT_QUESTION_INSTRUCTIONS
            self.continue_topic_agent.instructions = NEXT_QUESTION_INSTRUCTIONS

            # Continue with the current topic with properly formatted prompt including empathetic_response
            continue_topic_query = CONTINUE_TOPIC_PROMPT.format(
                conversation_history=history_text,
                employee_data=self.employee_data,
                context=self.context,
                current_topic=self.current_topic if self.current_topic else "general well-being",
                empathetic_response=empathetic_response
            )

            response = self.continue_topic_agent.run(continue_topic_query)
            response_text = self._get_response_text(response)
            next_question = self._extract_question(response_text)

        # Add the new question to conversation history
        self.conversation_history.append(
            {"role": "counselor", "content": next_question}
        )

        # Return the next question (empathetic response already included in the templates)
        return f"{empathetic_response} {response_text}"

    def _extract_question(self, text):
        """Extract the question from the model response"""
        # Remove prefix markers if present
        if text.startswith("COMPLETE:"):
            text = text[len("COMPLETE:") :].strip()
        elif text.startswith("ESCALATED_TO_HR:"):
            text = text[len("ESCALATED_TO_HR:") :].strip()

        # Simple heuristic: look for sentence ending with question mark
        sentences = re.split(r"(?<=[.!?])\s+", text)
        for sentence in sentences:
            if "?" in sentence:
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
        history_text = "\n".join(
            [
                f"{'Counselor' if item['role'] == 'counselor' else 'Employee'}: {item['content']}"
                for item in self.conversation_history
            ]
        )

        # Limit history to avoid token limits
        history_text = history_text[:1500]  # Limit the history to 1500 characters

        # Create the query for report generation
        query = REPORT_GENERATION_QUERY.format(
            conversation_history=history_text,
            employee_data=self.employee_data,
            context=self.context,
        )

        # Generate the report using the report_agent
        response = self.report_agent.run(query)
        return self._get_response_text(response)

    def is_escalated(self):
        """
        Check if the conversation was escalated to HR.

        Returns:
            True if the conversation was escalated to HR, False otherwise
        """
        return self.is_escalated_to_hr
