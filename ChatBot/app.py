import os
import config
import traceback  # Add this import
from dotenv import load_dotenv
import os
# Try the updated version first, if it fails, use the simpler version
try:
    from knowledge_base import KnowledgeBaseManager
except TypeError:
    print("Using simple knowledge base manager without chunking parameters...")
    from knowledge_base import KnowledgeBaseManager

from counseling_agent import CounselingAgent
from conversation_manager import ConversationManager

def main():
    try:  # Add overall try-except block
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

        load_dotenv()  # Load environment variables from .env file
        # Initialize counseling agent
        print("Initializing counseling agent...")
        os.getenv("OPENAI_API_KEY")
            
        counseling_agent = CounselingAgent(
            model_id=config.MODEL_ID,
            # api_key=openai_api_key,
            kb_manager=kb_manager,
            system_prompt=config.CUSTOM_SYSTEM_PROMPT
        )
        
        # Initialize conversation manager
        conversation_manager = ConversationManager(counseling_agent)
        
        # Start the conversation
        print("\n----- Starting Counseling Session -----\n")
        
        try:  # Add try-except around conversation start
            current_question = conversation_manager.start_conversation()
            print(f"Successfully started conversation with initial question: {current_question[:50]}...")
        except Exception as e:
            print(f"Error starting conversation: {str(e)}")
            print(traceback.format_exc())
            return
        
        # Main conversation loop
        while not conversation_manager.is_conversation_complete():
            try:  # Add try-except in the conversation loop
                print(f"Counselor: {current_question}")
                user_response = input("Employee: ")
                
                # Exit command
                if user_response.lower() in ["exit", "quit", "stop"]:
                    print("Counseling session terminated by user.")
                    return
                
                print("Processing your response...")
                current_question = conversation_manager.handle_response(user_response)
                print("Response processed successfully.")
                print()  # Add a blank line for readability
            except Exception as e:
                print(f"Error during conversation: {str(e)}")
                print(traceback.format_exc())
                print("Would you like to try again or exit? (try/exit)")
                choice = input().lower()
                if choice != "try":
                    return
        
        print(current_question)  # Print the completion message
        
        # Generate and display the report
        print("\n----- Generating Comprehensive Report -----\n")
        try:  # Add try-except around report generation
            report = conversation_manager.generate_final_report()
            print(report)
            
            # Save the report to a file
            with open("employee_counseling_report.md", "w") as f:
                f.write(report)
            
            print("\nReport saved to 'employee_counseling_report.md'")
        except Exception as e:
            print(f"Error generating report: {str(e)}")
            print(traceback.format_exc())
    
    except Exception as e:  # Catch any other exceptions
        print(f"An unexpected error occurred: {str(e)}")
        print(traceback.format_exc())

if __name__ == "__main__":
    main()