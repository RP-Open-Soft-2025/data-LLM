class ConversationManager:
    def __init__(self, counseling_agent):
        """
        Initialize the conversation manager.
        
        Args:
            counseling_agent: An instance of the CounselingAgent
        """
        self.agent = counseling_agent
        self.is_complete = False
    
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
            The next question or None if the conversation is complete
        """
        next_question = self.agent.process_response(user_response)
        
        if next_question is None:
            self.is_complete = True
            return "Thank you for your responses. I now have enough information to generate a comprehensive report."
        else:
            return next_question
    
    def is_conversation_complete(self):
        """Check if the conversation is complete"""
        return self.is_complete
    
    def generate_final_report(self):
        """Generate the final report"""
        if not self.is_complete:
            raise ValueError("Cannot generate report before conversation is complete")
        
        return self.agent.generate_report()