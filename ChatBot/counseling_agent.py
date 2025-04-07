from agno.agent import Agent
from agno.models.groq import Groq
import re
from agno.models.google import Gemini
from agno.models.openai import OpenAIChat
from agno.tools.thinking import ThinkingTools
from .prompt_templates1 import (
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
)
from dotenv import load_dotenv
import os
from . import config
import re

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
        self.kb_manager = kb_manager
        self.context = context if context else ""

        # Set up the model
        api_key = os.getenv("OPENAI_API_KEY")
        model = OpenAIChat(id=model_id, api_key=api_key)

        # Initialize specialized agents for different tasks
        self.initial_agent = Agent(
            model=model,
            add_history_to_messages=True,
            # Number of historical responses to add to the messages.
            num_history_responses=15,
            description=INITIAL_QUESTION_DESCRIPTION,
            instructions=INITIAL_QUESTION_INSTRUCTIONS,
            tools=[ThinkingTools()],
            markdown=True,
        )

        self.context_agent = Agent(
            model=model,
            add_history_to_messages=True,
            # Number of historical responses to add to the messages.
            num_history_responses=15,
            description=CONTEXT_QUESTION_DESCRIPTION,
            instructions=CONTEXT_QUESTION_INSTRUCTIONS,
            tools=[ThinkingTools()],
            markdown=True,
        )

        # We'll initialize next_question_agent in process_response
        # to format the instructions with actual conversation history and employee data
        self.next_question_agent = None

        self.report_agent = Agent(
            model=model,
            add_history_to_messages=True,
            # Number of historical responses to add to the messages.
            num_history_responses=15,
            description=REPORT_GENERATION_DESCRIPTION,
            instructions=REPORT_GENERATION_INSTRUCTIONS,
            tools=[ThinkingTools()],
            markdown=True,
        )

        # Prepare employee data
        if report_file_path:
            with open(report_file_path, "r") as file:
                self.employee_data = file.read()
        else:
            with open(config.EMPLOYEE_DATA_PATH, "r") as file:
                self.employee_data = file.read()

        # Extract and store issues from employee data
        self.issues = self._extract_issues_from_data()
        self.current_topic = None
        self.topic_questions_count = {}  # Track questions per topic
        self.explored_topics = set()  # Keep track of fully explored topics

        # Retrieve relevant question templates
        search_query = f"""
        Summary of chat history of an employee's counselling sessions (note that this can be empty):
        {context}

        The most appropriate questions to ask the given employee based on the context:
        """
        self.question_templates = self.kb_manager.retrieve_from_questions(
            search_query, num_documents=1
        )

        self.conversation_history = []
        self.is_interview_complete = False
        self.is_escalated_to_hr = False

        # Store the model reference for creating agents later
        self.model = model

    def _extract_issues_from_data(self):
        """Extract the main issues from employee data"""
        issues = []
        # Looking for issue patterns like "Issue 1:", "Issue 2:", etc.
        issue_pattern = r"Issue \d+:(.*?)(?=Issue \d+:|$)"
        matches = re.findall(issue_pattern, self.employee_data, re.DOTALL)

        if matches:
            for match in matches:
                issues.append(match.strip())
        else:
            # Fallback: try to find "**Issue" format
            issue_pattern = r"\*\*Issue \d+:(.*?)(?=\*\*Issue \d+:|$)"
            matches = re.findall(issue_pattern, self.employee_data, re.DOTALL)
            if matches:
                for match in matches:
                    issues.append(match.strip())

        return issues if issues else ["general well-being"]  # Fallback topic

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

        # Set the initial topic as the first issue
        if self.issues:
            self.current_topic = self.issues[0]
            self.topic_questions_count[self.current_topic] = 1

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

        # Determine if we need to change topics based on question count
        if self.current_topic and self.current_topic in self.topic_questions_count:
            if (
                self.topic_questions_count[self.current_topic] >= 4
            ):  # Max questions per topic
                self.explored_topics.add(self.current_topic)
                # Find a new unexplored topic
                for topic in self.issues:
                    if topic not in self.explored_topics:
                        self.current_topic = topic
                        self.topic_questions_count[self.current_topic] = 0
                        break
                # If all topics explored, mark interview as complete
                if all(topic in self.explored_topics for topic in self.issues):
                    self.is_interview_complete = True
                    return None

        # Update agent with topic tracking information
        topic_status = f"""
        TOPIC TRACKING:
        - Current topic: {self.current_topic}
        - Questions asked on current topic: {self.topic_questions_count.get(self.current_topic, 0)}
        - Topics explored: {', '.join(self.explored_topics) if self.explored_topics else 'None'}
        - Remaining topics: {', '.join(topic for topic in self.issues if topic not in self.explored_topics)}
        
        REMEMBER: MUST change topics after 4 questions.
        """

        # Format the NEXT_QUESTION_INSTRUCTIONS with current conversation history and employee data
        formatted_instructions = []
        for instruction in NEXT_QUESTION_INSTRUCTIONS:
            formatted_instructions.append(
                instruction.format(
                    conversation_history=history_text, employee_data=self.employee_data
                )
            )

        # Add the topic tracking information to instructions
        formatted_instructions.append(topic_status)

        # Create or update the next_question_agent with formatted instructions
        self.next_question_agent = Agent(
            model=self.model,
            add_history_to_messages=True,
            num_history_responses=15,
            description=NEXT_QUESTION_DESCRIPTION,
            instructions=formatted_instructions,
            tools=[ThinkingTools()],
            markdown=True,
        )

        # Create the query for next question generation
        query = (
            NEXT_QUESTION_QUERY.format(
                conversation_history=history_text,
                employee_data=self.employee_data,
                question_templates=self.question_templates,
                context=self.context,
            )
            + "\n"
            + topic_status
        )

        # Generate the next question using the next_question_agent
        response = self.next_question_agent.run(query)
        response_text = self._get_response_text(response)

        if response_text.startswith('"COMPLETE:') or response_text.startswith(
            "COMPLETE:"
        ):
            self.is_interview_complete = True
            return None
        elif response_text.startswith('"ESCALATED_TO_HR:') or response_text.startswith(
            "ESCALATED_TO_HR:"
        ):
            self.is_interview_complete = True
            self.is_escalated_to_hr = True
            return None
        elif response_text.startswith("CONTINUE:"):
            next_question = response_text.replace("CONTINUE:", "").strip()
            self.conversation_history.append(
                {"role": "counselor", "content": next_question}
            )
            # Update question count for current topic
            if self.current_topic:
                self.topic_questions_count[self.current_topic] = (
                    self.topic_questions_count.get(self.current_topic, 0) + 1
                )
            return next_question
        else:
            # If the model doesn't follow the format, extract the likely question
            next_question = self._extract_question(response_text)
            self.conversation_history.append(
                {"role": "counselor", "content": next_question}
            )
            # Update question count for current topic
            if self.current_topic:
                self.topic_questions_count[self.current_topic] = (
                    self.topic_questions_count.get(self.current_topic, 0) + 1
                )
            return next_question

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
