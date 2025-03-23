import os
import config
# Try the updated version first, if it fails, use the simpler version
try:
    from knowledge_base import KnowledgeBaseManager
except TypeError:
    print("Using simple knowledge base manager without chunking parameters...")
    from knowledge_base_simple import KnowledgeBaseManager

from counseling_agent import CounselingAgent
from conversation_manager import ConversationManager

def main():
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
    
    # Initialize counseling agent
    print("Initializing counseling agent...")
    counseling_agent = CounselingAgent(
        model_id=config.MODEL_ID,
        api_key=config.GROQ_API_KEY,
        kb_manager=kb_manager,
        system_prompt=config.CUSTOM_SYSTEM_PROMPT
    )
    
    # Initialize conversation manager
    conversation_manager = ConversationManager(counseling_agent)
    
    # Start the conversation
    print("\n----- Starting Counseling Session -----\n")
    
    current_question = conversation_manager.start_conversation()
    
    # Main conversation loop
    while not conversation_manager.is_conversation_complete():
        print(f"Counselor: {current_question}")
        user_response = input("Employee: ")
        
        # Exit command
        if user_response.lower() in ["exit", "quit", "stop"]:
            print("Counseling session terminated by user.")
            return
        
        current_question = conversation_manager.handle_response(user_response)
        print()  # Add a blank line for readability
    
    print(current_question)  # Print the completion message
    
    # Generate and display the report
    print("\n----- Generating Comprehensive Report -----\n")
    report = conversation_manager.generate_final_report()
    
    print(report)
    
    # Save the report to a file
    with open("employee_counseling_report.md", "w") as f:
        f.write(report)
    
    print("\nReport saved to 'employee_counseling_report.md'")

if __name__ == "__main__":
    main()