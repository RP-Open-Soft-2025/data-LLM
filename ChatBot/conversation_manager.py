class ConversationManager:
    def __init__(self, counseling_agent):
        """
        Initialize the conversation manager.

        Args:
            counseling_agent: An instance of the CounselingAgent
        """
        self.agent = counseling_agent
        self.is_complete = False
        self.is_escalated = False

    def start_conversation(self):
        """Start the counseling conversation"""
        initial_question = self.agent.start_interview()
        return initial_question

    def handle_response(self, user_response):
        """
        Process the user's response and get the next question.

        Args:
            user_response: The user's response to the previous question

        Returns:
            The next question or None if the conversation is complete or escalated
        """
        next_question = self.agent.process_response(user_response)

        if next_question is None:
            self.is_complete = True
            self.is_escalated = self.agent.is_escalated()

            if self.is_escalated:
                return "This conversation needs immediate attention from HR. I'll make sure your concerns are addressed promptly. Thank you for sharing your experiences."
            else:
                return "Thank you for your responses. I now have enough information to generate a comprehensive report."
        else:
            return next_question

    def is_conversation_complete(self):
        """Check if the conversation is complete"""
        return self.is_complete

    def is_conversation_escalated(self):
        """Check if the conversation was escalated to HR"""
        return self.is_escalated

    def generate_final_report(self):
        """Generate the final report"""
        if not self.is_complete:
            raise ValueError("Cannot generate report before conversation is complete")

        report_text = self.agent.generate_report()

        # Add report header based on conversation outcome
        if self.is_escalated:
            header = "# ESCALATED TO HR: Employee Well-Being Report\n\n"
            header += "**URGENT: This case has been escalated to HR for immediate follow-up due to signs of severe distress.**\n\n"
        else:
            header = "# Employee Well-Being Report\n\n"

        return header + report_text
