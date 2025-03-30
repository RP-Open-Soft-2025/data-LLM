import streamlit as st
import os
import config
import time
from dotenv import load_dotenv

# Try the updated version first, if it fails, use the simpler version
try:
    from knowledge_base import KnowledgeBaseManager
except TypeError:
    st.warning("Using simple knowledge base manager without chunking parameters...")
    from knowledge_base import KnowledgeBaseManager

from counseling_agent import CounselingAgent
from conversation_manager import ConversationManager

def initialize_session_state():
    """Initialize session state variables if they don't exist"""
    if 'conversation_manager' not in st.session_state:
        st.session_state.conversation_manager = None
    if 'current_question' not in st.session_state:
        st.session_state.current_question = ""
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    if 'conversation_started' not in st.session_state:
        st.session_state.conversation_started = False
    if 'report_generated' not in st.session_state:
        st.session_state.report_generated = False
    if 'conversation_complete' not in st.session_state:
        st.session_state.conversation_complete = False

def initialize_system():
    """Initialize the counseling system components"""
    try:
        with st.spinner("Initializing Counseling Agent System..."):
            # Check if required files exist
            if not os.path.exists(config.EMPLOYEE_DATA_PATH):
                st.error(f"Error: Employee data file not found at {config.EMPLOYEE_DATA_PATH}")
                return False
            
            if not os.path.exists(config.QUESTIONS_PDF_PATH):
                st.error(f"Error: Questions PDF file not found at {config.QUESTIONS_PDF_PATH}")
                return False
            
            # Initialize knowledge bases
            kb_manager = KnowledgeBaseManager(
                employee_data_path=config.EMPLOYEE_DATA_PATH,
                questions_pdf_path=config.QUESTIONS_PDF_PATH,
                db_uri=config.DB_URI
            )
            
            # Load knowledge bases - will skip if already loaded
            kb_manager.load_knowledge_bases(force_reload=False)
            
            # Load environment variables
            load_dotenv()
            
            # Initialize counseling agent
            counseling_agent = CounselingAgent(
                model_id=config.MODEL_ID,
                kb_manager=kb_manager,
                system_prompt=config.CUSTOM_SYSTEM_PROMPT
            )
            
            # Initialize conversation manager
            st.session_state.conversation_manager = ConversationManager(counseling_agent)
            
            return True
            
    except Exception as e:
        st.error(f"An error occurred during initialization: {str(e)}")
        return False

def start_conversation():
    """Start the conversation with the counseling agent"""
    try:
        with st.spinner("Starting counseling session..."):
            current_question = st.session_state.conversation_manager.start_conversation()
            st.session_state.current_question = current_question
            st.session_state.messages.append({"role": "assistant", "content": current_question})
            st.session_state.conversation_started = True
            return True
    except Exception as e:
        st.error(f"Error starting conversation: {str(e)}")
        return False

def process_user_input(user_input):
    """Process the user's input and get the next question"""
    if user_input:
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": user_input})
        
        # Process the response
        with st.spinner("Processing your response..."):
            try:
                next_question = st.session_state.conversation_manager.handle_response(user_input)
                st.session_state.current_question = next_question
                
                # Add assistant response to chat history
                st.session_state.messages.append({"role": "assistant", "content": next_question})
                
                # Check if conversation is complete
                if st.session_state.conversation_manager.is_conversation_complete():
                    st.session_state.conversation_complete = True
            except Exception as e:
                st.error(f"Error processing response: {str(e)}")

def generate_report():
    """Generate the final counseling report"""
    try:
        with st.spinner("Generating comprehensive report..."):
            report = st.session_state.conversation_manager.generate_final_report()
            
            # Save the report to a file
            with open("employee_counseling_report.md", "w", encoding="utf-8") as f:
                f.write(report)
                
            st.session_state.final_report = report
            st.session_state.report_generated = True
            return True
    except Exception as e:
        st.error(f"Error generating report: {str(e)}")
        return False

def main():
    st.set_page_config(
        page_title="Employee Counseling System",
        page_icon="💬",
        layout="centered",
    )
    
    st.title("Employee Counseling System")
    
    # Initialize session state
    initialize_session_state()
    
    # Sidebar
    with st.sidebar:
        st.header("About")
        st.info("This is an AI-powered counseling system for employees. Answer the questions truthfully to receive a personalized counseling report.")
        
        if not st.session_state.conversation_started:
            if st.button("Start Counseling Session"):
                if initialize_system():
                    start_conversation()
        
        if st.session_state.conversation_started and st.session_state.conversation_complete and not st.session_state.report_generated:
            if st.button("Generate Report"):
                generate_report()
        
        if st.session_state.report_generated:
            st.success("Report generated successfully!")
            st.download_button(
                label="Download Report",
                data=st.session_state.final_report,
                file_name="employee_counseling_report.md",
                mime="text/markdown"
            )
    
    # Main chat area
    if st.session_state.conversation_started:
        # Display chat messages
        chat_container = st.container()
        with chat_container:
            for msg in st.session_state.messages:
                if msg["role"] == "assistant":
                    st.chat_message("assistant", avatar="🧠").write(msg["content"])
                else:
                    st.chat_message("user", avatar="👤").write(msg["content"])
        
        # Input box for user (only show if conversation is not complete)
        if not st.session_state.conversation_complete:
            user_input = st.chat_input("Your response")
            if user_input:
                process_user_input(user_input)
                st.rerun()
        elif not st.session_state.report_generated:
            st.info("Conversation complete. You can now generate your report from the sidebar.")
    else:
        st.info("Click 'Start Counseling Session' in the sidebar to begin.")
    
    # Display the report if generated
    if st.session_state.report_generated:
        with st.expander("View Counseling Report", expanded=True):
            st.markdown(st.session_state.final_report)

if __name__ == "__main__":
    main()