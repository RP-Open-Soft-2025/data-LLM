class ConversationManager:
    def __init__(self, counseling_agent, question_prompt=None, next_question_prompt=None, 
                 suggestion_prompt=None, follow_up_prompt=None, new_suggestion_prompt=None, 
                 report_prompt=None):
        """
        Initialize the conversation manager.
        
        Args:
            counseling_agent: An instance of the CounselingAgent
            question_prompt: Template for generating initial questions (optional)
            next_question_prompt: Template for generating personalized follow-up questions (optional)
            suggestion_prompt: Template for generating suggestions (optional)
            follow_up_prompt: Template for generating follow-up questions (optional)
            new_suggestion_prompt: Template for generating new suggestions (optional)
            report_prompt: Template for generating the final report (optional)
        """
        self.agent = counseling_agent
        self.is_complete = False
        self.state = "introduction"  # States: introduction, initial_questions, suggestions, follow_up, reporting
        self.current_question_index = 0
        self.current_follow_up_index = 0
        self.waiting_for_feedback = False
        self.follow_up_questions = []
        
        # Pass prompt templates to the agent if provided
        if question_prompt and hasattr(self.agent, 'set_question_prompt'):
            self.agent.set_question_prompt(question_prompt)
            
        if next_question_prompt and hasattr(self.agent, 'set_next_question_prompt'):
            self.agent.set_next_question_prompt(next_question_prompt)
            
        if suggestion_prompt and hasattr(self.agent, 'set_suggestion_prompt'):
            self.agent.set_suggestion_prompt(suggestion_prompt)
            
        if follow_up_prompt and hasattr(self.agent, 'set_follow_up_prompt'):
            self.agent.set_follow_up_prompt(follow_up_prompt)
            
        if new_suggestion_prompt and hasattr(self.agent, 'set_new_suggestion_prompt'):
            self.agent.set_new_suggestion_prompt(new_suggestion_prompt)
            
        if report_prompt and hasattr(self.agent, 'set_report_prompt'):
            self.agent.set_report_prompt(report_prompt)
    
    def start_conversation(self):
        """
        Start the counseling conversation
        
        Returns:
            Initial introduction message about the 7 questions
        """
        # Use the agent's method for generating initial questions
        if hasattr(self.agent, 'generate_initial_questions'):
            introduction = self.agent.generate_initial_questions()
            self.state = "initial_questions"
            return introduction
        else:
            # Fall back to the original method if generate_initial_questions doesn't exist
            initial_question = self.agent.start_interview()
            return initial_question
    
    def get_next_question(self):
        """
        Get the next personalized question in the sequence.
        
        Returns:
            The next personalized question to ask, or None if no question is available
        """
        if self.state == "initial_questions":
            # Make sure the agent has the get_next_question method
            if hasattr(self.agent, 'get_next_question'):
                return self.agent.get_next_question()
            else:
                # If the agent doesn't support the new flow, return None
                return None
        elif self.state == "follow_up" and self.current_follow_up_index < len(self.follow_up_questions):
            # Return the current follow-up question
            return self.follow_up_questions[self.current_follow_up_index]
        else:
            # No question is available in the current state
            return None
    
    def record_response(self, question_number, response):
        """
        Record the employee's response to a question in the initial phase.
        
        Args:
            question_number: The number of the question being answered (1-7)
            response: The employee's response to the question
        """
        if hasattr(self.agent, 'record_response'):
            self.agent.record_response(question_number, response)
    
    def generate_suggestions(self):
        """
        Generate suggestions based on the conversation so far.
        
        Returns:
            List of 3 suggestions
        """
        if hasattr(self.agent, 'generate_suggestions'):
            suggestions = self.agent.generate_suggestions()
            self.state = "suggestions"
            self.waiting_for_feedback = True
            return suggestions
        return []
    
    def extract_accepted_suggestions(self, response):
        """
        Extract which suggestions were accepted from the response.
        
        Args:
            response: The employee's response about suggestions
            
        Returns:
            List of accepted suggestion indices
        """
        if hasattr(self.agent, 'extract_accepted_suggestions'):
            return self.agent.extract_accepted_suggestions(response)
        return []
    
    def set_accepted_suggestions(self, indices):
        """
        Set which suggestions were accepted by the employee.
        
        Args:
            indices: List of suggestion indices that were accepted
        """
        if hasattr(self.agent, 'set_accepted_suggestions'):
            self.agent.set_accepted_suggestions(indices)
    
    def generate_follow_up_questions(self):
        """
        Generate follow-up questions when the employee isn't satisfied.
        
        Returns:
            List of follow-up questions
        """
        if hasattr(self.agent, 'generate_follow_up_questions'):
            # Don't add questions to conversation history in the agent since we'll handle that here
            questions = self.agent.generate_follow_up_questions(add_to_history=False)
            self.state = "follow_up"
            self.follow_up_questions = questions
            self.current_follow_up_index = 0
            return questions
        return []
    
    def record_follow_up_response(self, question, response):
        """
        Record the employee's response to a follow-up question.
        
        Args:
            question: The follow-up question
            response: The employee's response
        """
        if hasattr(self.agent, 'record_follow_up_response'):
            self.agent.record_follow_up_response(question, response)
    
    def generate_new_suggestions(self):
        """
        Generate new suggestions after follow-up questions.
        
        Returns:
            List of new suggestions
        """
        if hasattr(self.agent, 'generate_new_suggestions'):
            new_suggestions = self.agent.generate_new_suggestions()
            self.state = "new_suggestions"
            self.waiting_for_feedback = True
            return new_suggestions
        return []
    
    def handle_response(self, user_response):
        """
        Process the user's response and determine the next step based on the conversation state.
        
        Args:
            user_response: The user's response to the previous question/prompt
            
        Returns:
            The next question, suggestion, or message
        """
        # Check if the agent supports the new conversation flow
        if hasattr(self.agent, 'record_response'):
            # New conversation flow
            if self.state == "introduction":
                # We shouldn't reach this state as the introduction doesn't wait for response
                self.state = "initial_questions"
                return self.get_next_question()
                
            elif self.state == "initial_questions":
                # Handle responses to the 7 initial questions
                self.agent.record_response(self.current_question_index + 1, user_response)
                self.current_question_index += 1
                
                if self.current_question_index < 7:
                    # Get the next personalized question from the initial set
                    next_question = self.get_next_question()
                    if next_question:
                        return next_question
                    else:
                        # If there's no next question, move to suggestions
                        self.state = "suggestions"
                        suggestions = self.agent.generate_suggestions()
                        return self._format_suggestions(suggestions)
                else:
                    # After 7 questions, move to suggestions
                    self.state = "suggestions"
                    suggestions = self.agent.generate_suggestions()
                    return self._format_suggestions(suggestions)
                    
            elif self.state == "suggestions" and self.waiting_for_feedback:
                # Handle the user's feedback on the suggestions
                self.waiting_for_feedback = False
                
                # Use the improved satisfaction detection method
                if hasattr(self.agent, 'is_satisfied_with_suggestions'):
                    is_satisfied, accepted_indices = self.agent.is_satisfied_with_suggestions(user_response)
                    if is_satisfied:
                        # They're satisfied, set the accepted suggestions
                        self.agent.set_accepted_suggestions(accepted_indices)
                        
                        # End the conversation
                        self.is_complete = True
                        return "Thank you for your feedback! I'll make sure these suggestions are passed to our employee experience team. I now have enough information to generate a comprehensive report."
                    else:
                        # They're not satisfied, generate personalized follow-up questions
                        self.state = "follow_up"
                        self.follow_up_questions = self.agent.generate_follow_up_questions()
                        self.current_follow_up_index = 0
                        
                        # Return the first follow-up question
                        if len(self.follow_up_questions) > 0:
                            return self.follow_up_questions[0]
                        else:
                            # If no follow-up questions were generated, try new suggestions anyway
                            self.state = "new_suggestions"
                            new_suggestions = self.agent.generate_new_suggestions()
                            return self._format_suggestions(new_suggestions, is_new=True)
                else:
                    # Fall back to the simpler method if is_satisfied_with_suggestions doesn't exist
                    # This block is kept for compatibility but won't be used with the updated CounselingAgent
                    response_lower = user_response.lower()
                    if "yes" in response_lower and "not" not in response_lower:
                        accepted_indices = self.agent.extract_accepted_suggestions(user_response)
                        self.agent.set_accepted_suggestions(accepted_indices)
                        self.is_complete = True
                        return "Thank you for your feedback! I'll make sure these suggestions are passed to our employee experience team. I now have enough information to generate a comprehensive report."
                    elif "satisfied" in response_lower and "not satisfied" not in response_lower and "not" not in response_lower[:response_lower.find("satisfied")]:
                        accepted_indices = self.agent.extract_accepted_suggestions(user_response)
                        self.agent.set_accepted_suggestions(accepted_indices)
                        self.is_complete = True
                        return "Thank you for your feedback! I'll make sure these suggestions are passed to our employee experience team. I now have enough information to generate a comprehensive report."
                    else:
                        # They're not satisfied, generate personalized follow-up questions
                        self.state = "follow_up"
                        self.follow_up_questions = self.agent.generate_follow_up_questions()
                        self.current_follow_up_index = 0
                        
                        # Return the first follow-up question
                        if len(self.follow_up_questions) > 0:
                            return self.follow_up_questions[0]
                        else:
                            # If no follow-up questions were generated, try new suggestions anyway
                            self.state = "new_suggestions"
                            new_suggestions = self.agent.generate_new_suggestions()
                            return self._format_suggestions(new_suggestions, is_new=True)
                    
            elif self.state == "follow_up":
                # Handle responses to follow-up questions
                if self.current_follow_up_index < len(self.follow_up_questions):
                    # Record their response to the current follow-up question
                    self.agent.record_follow_up_response(
                        self.follow_up_questions[self.current_follow_up_index], 
                        user_response
                    )
                    
                    self.current_follow_up_index += 1
                    
                    # If we have more follow-up questions, ask the next one
                    if self.current_follow_up_index < len(self.follow_up_questions):
                        return self.follow_up_questions[self.current_follow_up_index]
                    else:
                        # After all follow-up questions, generate new personalized suggestions
                        self.state = "new_suggestions"
                        new_suggestions = self.agent.generate_new_suggestions()
                        return self._format_suggestions(new_suggestions, is_new=True)
                
            elif self.state == "new_suggestions" and self.waiting_for_feedback:
                # Handle feedback on the new suggestions
                self.waiting_for_feedback = False
                
                # Use the improved satisfaction detection method
                if hasattr(self.agent, 'is_satisfied_with_suggestions'):
                    is_satisfied, accepted_indices = self.agent.is_satisfied_with_suggestions(user_response)
                    if is_satisfied:
                        # They're satisfied, set the accepted suggestions
                        self.agent.set_accepted_suggestions(accepted_indices)
                        
                        # End the conversation
                        self.is_complete = True
                        return "Thank you for your feedback! I'll make sure these suggestions are passed to our employee experience team. I now have enough information to generate a comprehensive report."
                    else:
                        # Start another round of personalized follow-up questions
                        self.state = "follow_up"
                        self.follow_up_questions = self.agent.generate_follow_up_questions()
                        self.current_follow_up_index = 0
                        
                        # Return the first follow-up question
                        if len(self.follow_up_questions) > 0:
                            return self.follow_up_questions[0]
                        else:
                            # If no follow-up questions were generated, try new suggestions anyway
                            self.state = "new_suggestions"
                            new_suggestions = self.agent.generate_new_suggestions()
                            return self._format_suggestions(new_suggestions, is_new=True)
                else:
                    # Fall back to the simpler method if is_satisfied_with_suggestions doesn't exist
                    response_lower = user_response.lower()
                    if "yes" in response_lower and "not" not in response_lower:
                        accepted_indices = self.agent.extract_accepted_suggestions(user_response)
                        self.agent.set_accepted_suggestions(accepted_indices)
                        self.is_complete = True
                        return "Thank you for your feedback! I'll make sure these suggestions are passed to our employee experience team. I now have enough information to generate a comprehensive report."
                    elif "satisfied" in response_lower and "not satisfied" not in response_lower and "not" not in response_lower[:response_lower.find("satisfied")]:
                        accepted_indices = self.agent.extract_accepted_suggestions(user_response)
                        self.agent.set_accepted_suggestions(accepted_indices)
                        self.is_complete = True
                        return "Thank you for your feedback! I'll make sure these suggestions are passed to our employee experience team. I now have enough information to generate a comprehensive report."
                    else:
                        # Start another round of personalized follow-up questions
                        self.state = "follow_up"
                        self.follow_up_questions = self.agent.generate_follow_up_questions()
                        self.current_follow_up_index = 0
                        
                        # Return the first follow-up question
                        if len(self.follow_up_questions) > 0:
                            return self.follow_up_questions[0]
                        else:
                            # If no follow-up questions were generated, try new suggestions anyway
                            self.state = "new_suggestions"
                            new_suggestions = self.agent.generate_new_suggestions()
                            return self._format_suggestions(new_suggestions, is_new=True)
        else:
            # Fall back to the original conversation flow
            next_question = self.agent.process_response(user_response)
            
            if next_question is None:
                self.is_complete = True
                return "Thank you for your responses. I now have enough information to generate a comprehensive report."
            else:
                return next_question
        
        # If we get here, something went wrong - try to recover with a personalized question
        return "I apologize for the confusion. Let's continue our conversation. Based on what you've shared so far, what specific aspect of your work situation would you like to discuss next?"
    
    def _format_suggestions(self, suggestions, is_new=False):
        """
        Format suggestions as a nice message.
        
        Args:
            suggestions: List of suggestions
            is_new: Whether these are new suggestions
            
        Returns:
            Formatted string with suggestions
        """
        prefix = "New " if is_new else ""
        context = "this additional information" if is_new else "our conversation"
        suggestions_text = f"Based on {context}, here are {'new ' if is_new else ''}suggestions that I believe would specifically help in your situation:\n\n"
        
        for i, suggestion in enumerate(suggestions, 1):
            suggestions_text += f"{prefix}Suggestion {i}: {suggestion}\n"
        
        suggestions_text += "\nAre you satisfied with at least 2 of these suggestions? If yes, which ones? If not, I'd be happy to continue our conversation."
        self.waiting_for_feedback = True
        return suggestions_text
    
    def is_conversation_complete(self):
        """Check if the conversation is complete"""
        return self.is_complete
    
    def generate_final_report(self):
        """Generate the final report"""
        if not self.is_complete:
            raise ValueError("Cannot generate report before conversation is complete")
        
        return self.agent.generate_report()