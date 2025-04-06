class ConversationManager:
    def __init__(self, counseling_agent):
        """
        Initialize the conversation manager.

        Args:
            counseling_agent: An instance of the CounselingAgent
        """
        if not counseling_agent:
            raise ValueError("Counseling agent must be provided")

        self.agent = counseling_agent
        self.is_complete = False
        self.is_escalated = False

    def start_conversation(self):
        """Start the counseling conversation"""
        try:
            initial_question = self.agent.start_interview()
            if not initial_question:
                raise RuntimeError("Counseling agent failed to provide an initial question.")
            return initial_question
        except Exception as e:
            return f"Error starting conversation: {str(e)}"

    def handle_response(self, user_response):
        """
        Process the user's response and get the next question.

        Args:
            user_response: The user's response to the previous question

        Returns:
            The next question or a closing message if the conversation is complete or escalated
        """
        if not isinstance(user_response, str) or not user_response.strip():
            return "Invalid response. Please provide a non-empty message."

        try:
            next_question = self.agent.process_response(user_response)

            if next_question is None:
                self.is_complete = True

                try:
                    self.is_escalated = self.agent.is_escalated()
                except Exception as e:
                    return f"Error determining escalation status: {str(e)}"

                if self.is_escalated:
                    return (
                        "This conversation needs immediate attention from HR. "
                        "I'll make sure your concerns are addressed promptly. "
                        "Thank you for sharing your experiences."
                    )
                else:
                    return (
                        "Thank you for your responses. I now have enough information "
                        "to generate a comprehensive report."
                    )
            else:
                return next_question

        except Exception as e:
            return f"Error handling response: {str(e)}"

    def is_conversation_complete(self):
        """Check if the conversation is complete"""
        return self.is_complete

    def is_conversation_escalated(self):
        """Check if the conversation was escalated to HR"""
        return self.is_escalated

    def generate_final_report(self):
        """
        Generate the final report.

        Raises:
            ValueError: If the conversation is not complete
            RuntimeError: If the agent fails to generate a report
        """
        if not self.is_complete:
            raise ValueError("Cannot generate report before conversation is complete")

        try:
            report_text = self.agent.generate_report()
        except Exception as e:
            raise RuntimeError(f"Failed to generate report: {str(e)}")

        # Add report header based on conversation outcome
        if self.is_escalated:
            header = "# ESCALATED TO HR: Employee Well-Being Report\n\n"
            header += "**URGENT: This case has been escalated to HR for immediate follow-up due to signs of severe distress.**\n\n"
        else:
            header = "# Employee Well-Being Report\n\n"

        return header + report_text
