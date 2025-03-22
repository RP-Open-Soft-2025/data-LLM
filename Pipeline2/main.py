import os
import sys
import traceback
from datetime import datetime
from dotenv import load_dotenv

from document_processor import DocumentProcessor
from vector_store import VectorStore
from conversation_tracker import ConversationTracker
from counseling_agent import CounselingAgent
from utils import create_session_summary, save_session_summary

def main():
    # Load environment variables
    load_dotenv()
    
    # Check for required API key
    groq_api_key = os.getenv("GROQ_API_KEY")
    if not groq_api_key:
        print("Error: GROQ_API_KEY not found in environment variables.")
        print("Please create a .env file with GROQ_API_KEY=your_api_key")
        return
    
    # Ask for file paths
    pdf_path = './Questions.pdf'
    txt_path = './employee_report.txt'
    
    # Check if files exist
    if not os.path.exists(pdf_path):
        print(f"Error: The PDF file '{pdf_path}' does not exist.")
        return
    
    if not os.path.exists(txt_path):
        print(f"Error: The TXT file '{txt_path}' does not exist.")
        return
    
    # Process documents
    try:
        print("\nProcessing documents...")
        doc_processor = DocumentProcessor()
        documents = doc_processor.process_documents(pdf_path, txt_path)
    except Exception as e:
        print(f"Error processing documents: {e}")
        traceback.print_exc()
        return
    
    # Create vector store
    try:
        print("Creating vector database...")
        vector_store = VectorStore()
        vector_store.add_documents(documents)
    except Exception as e:
        print(f"Error creating vector database: {e}")
        traceback.print_exc()
        return
    
    # Initialize conversation tracker
    conversation_tracker = ConversationTracker()
    
    # Ask for number of questions
    max_questions = 4
    
    # Initialize counseling agent
    try:
        print("\nInitializing counseling agent...")
        agent = CounselingAgent(
            vector_store=vector_store,
            conversation_tracker=conversation_tracker,
            groq_api_key=groq_api_key,
            max_questions=max_questions
        )
    except Exception as e:
        print(f"Error initializing counseling agent: {e}")
        traceback.print_exc()
        return
    
    # Run the counseling session
    try:
        print("\n=== Counseling Session Started ===\n")
        final_state = agent.run_session()
    except KeyboardInterrupt:
        print("\n\nSession interrupted by user.")
        return
    except Exception as e:
        print(f"\nError during counseling session: {e}")
        traceback.print_exc()
        return
    
    # Get the report
    report = final_state.get("report", "No report was generated.")
    print("\n=== Behavioral Report ===\n")
    print(report)
    
    # Save the session summary
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        session_summary = create_session_summary(
            report=report,
            conversation_history=conversation_tracker.get_conversation_history()
        )
        
        session_file = f"counseling_session_{timestamp}.json"
        save_session_summary(session_summary, session_file)
        print(f"\nSession summary saved to {session_file}")
    except Exception as e:
        print(f"Error saving session summary: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Unexpected error: {e}")
        traceback.print_exc()