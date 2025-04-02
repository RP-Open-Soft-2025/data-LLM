import os
import config
import traceback
from dotenv import load_dotenv
from prompt_templates import (
    COUNSELING_SYSTEM_PROMPT,
    QUESTION_GENERATION_PROMPT,
    NEXT_QUESTION_PROMPT,
    SUGGESTION_GENERATION_PROMPT,
    FOLLOW_UP_PROMPT,
    NEW_SUGGESTION_PROMPT,
    REPORT_GENERATION_PROMPT
)

# Try the updated version first, if it fails, use the simpler version
try:
    from knowledge_base import KnowledgeBaseManager
except TypeError:
    print("Using simple knowledge base manager without chunking parameters...")
    from knowledge_base import KnowledgeBaseManager

from counseling_agent import CounselingAgent
from conversation_manager import ConversationManager

def main():
    try:
        print("Initializing Counseling Agent System...")
        
        # Check if required files exist
        if not os.path.exists(config.EMPLOYEE_DATA_PATH):
            print(f"Error: Employee data file not found at {config.EMPLOYEE_DATA_PATH}")
            return
        
        if not os.path.exists(config.QUESTIONS_PDF_PATH):
            print(f"Error: Questions PDF file not found at {config.QUESTIONS_PDF_PATH}")
            return
        
        # Initialize knowledge bases
        print("Setting up knowledge bases...")
        kb_manager = KnowledgeBaseManager(
            employee_data_path=config.EMPLOYEE_DATA_PATH,
            questions_pdf_path=config.QUESTIONS_PDF_PATH,
            db_uri=config.DB_URI
        )
        
        # Load knowledge bases - will skip if already loaded
        kb_manager.load_knowledge_bases(force_reload=False)
        
        # Import environment variables
        load_dotenv()
        
        # Initialize counseling agent
        print("Initializing counseling agent...")
        os.getenv("OPENAI_API_KEY")
            
        counseling_agent = CounselingAgent(
            model_id=config.MODEL_ID,
            kb_manager=kb_manager,
            system_prompt=COUNSELING_SYSTEM_PROMPT
        )
        
        # Initialize conversation manager with all prompt templates
        conversation_manager = ConversationManager(
            counseling_agent,
            question_prompt=QUESTION_GENERATION_PROMPT,
            next_question_prompt=NEXT_QUESTION_PROMPT,
            suggestion_prompt=SUGGESTION_GENERATION_PROMPT,
            follow_up_prompt=FOLLOW_UP_PROMPT,
            new_suggestion_prompt=NEW_SUGGESTION_PROMPT,
            report_prompt=REPORT_GENERATION_PROMPT
        )
        
        print("\n----- Starting Counseling Session -----\n")
        
        try:
            # Initialize the conversation with the introduction
            initial_message = conversation_manager.start_conversation()
            print(f"Counselor: {initial_message}")
            
            # Main conversation loop for initial questions
            for question_num in range(1, 8):
                # Get the next personalized question
                current_question = conversation_manager.get_next_question()
                print(f"Counselor: {current_question}")
                
                # Get and process the employee's response
                user_response = input("Employee: ")
                
                # Exit command check
                if user_response.lower() in ["exit", "quit", "stop"]:
                    print("Counseling session terminated by user.")
                    return
                
                print("Processing your response...")
                # Only record the response without advancing state yet
                conversation_manager.record_response(question_num, user_response)
                print("Response processed successfully.")
                print()  # Add a blank line for readability
            
            # After 7 questions, generate and show initial suggestions
            suggestions = conversation_manager.generate_suggestions()
            
            # Display suggestions
            print("Counselor: Based on our conversation, here are suggestions that I believe would specifically help in your situation:\n")
            for i, suggestion in enumerate(suggestions, 1):
                print(f"Suggestion {i}: {suggestion}")
            print("\nAre you satisfied with at least 2 of these suggestions? If yes, which ones? If not, I'd be happy to continue our conversation.")
            
            # Feedback and additional questions loop - continue until satisfied
            while not conversation_manager.is_conversation_complete():
                user_response = input("Employee: ")
                
                # Exit command check
                if user_response.lower() in ["exit", "quit", "stop"]:
                    print("Counseling session terminated by user.")
                    return
                
                print("Processing your response...")
                
                # Check if they're satisfied with the suggestions using the new method
                if conversation_manager.state in ["suggestions", "new_suggestions"] and conversation_manager.waiting_for_feedback:
                    is_satisfied, accepted_indices = counseling_agent.is_satisfied_with_suggestions(user_response)
                    
                    if is_satisfied:
                        # Set the accepted suggestions and move to report generation
                        conversation_manager.agent.set_accepted_suggestions(accepted_indices)
                        conversation_manager.is_complete = True
                        print("Counselor: Thank you for your feedback! I'll make sure these suggestions are passed to our employee experience team. I now have enough information to generate a comprehensive report.")
                    else:
                        # They're not satisfied, generate follow-up questions
                        follow_up_questions = conversation_manager.generate_follow_up_questions()
                        
                        # Ask follow-up questions one by one
                        for question in follow_up_questions:
                            print(f"Counselor: {question}")
                            follow_up_response = input("Employee: ")
                            
                            # Exit command check
                            if follow_up_response.lower() in ["exit", "quit", "stop"]:
                                print("Counseling session terminated by user.")
                                return
                                
                            conversation_manager.record_follow_up_response(question, follow_up_response)
                        
                        # After follow-up questions, generate new suggestions
                        new_suggestions = conversation_manager.generate_new_suggestions()
                        
                        # Display new suggestions
                        print("Counselor: Based on this additional information, here are new suggestions that might better address your situation:\n")
                        for i, suggestion in enumerate(new_suggestions, 1):
                            print(f"New Suggestion {i}: {suggestion}")
                        print("\nAre you satisfied with at least 2 of these suggestions? If yes, which ones? If not, I'd be happy to continue our conversation.")
                else:
                    # For other states, use the regular handle_response method
                    next_message = conversation_manager.handle_response(user_response)
                    if next_message:
                        print(f"Counselor: {next_message}")
                
                print("Response processed successfully.")
                print()  # Add a blank line for readability
            
            # Generate and display the report when conversation is complete
            print("\n----- Generating Comprehensive Report -----\n")
            report = conversation_manager.generate_final_report()
            print(report)
            
            # Save the report to a file
            with open("employee_counseling_report.md", "w") as f:
                f.write(report)
            
            print("\nReport saved to 'employee_counseling_report.md'")
            
        except Exception as e:
            print(f"Error during conversation: {str(e)}")
            print(traceback.format_exc())
            print("Would you like to try again or exit? (try/exit)")
            choice = input().lower()
            if choice != "try":
                return
    
    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")
        print(traceback.format_exc())

if __name__ == "__main__":
    main()