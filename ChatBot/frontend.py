import streamlit as st
import os
import config
import traceback
from dotenv import load_dotenv
from knowledge_base import KnowledgeBaseManager
from counseling_agent import CounselingAgent
from conversation_manager import ConversationManager
import time

# Set page config
st.set_page_config(
    page_title="Employee Counseling Assistant",
    page_icon="🤝",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for better styling
st.markdown(
    """
    <style>
    .stTextInput > div > div > input {
        background-color: #f0f2f6;
    }
    .stMarkdown {
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    .chat-message {
        padding: 1.5rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        display: flex;
        flex-direction: column;
    }
    .user-message {
        background-color: #e3f2fd;
        margin-left: 20%;
    }
    .assistant-message {
        background-color: #f5f5f5;
        margin-right: 20%;
    }
    </style>
""",
    unsafe_allow_html=True,
)


def initialize_session_state():
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "conversation_manager" not in st.session_state:
        st.session_state.conversation_manager = None
    if "initialized" not in st.session_state:
        st.session_state.initialized = False
    if "input_key" not in st.session_state:
        st.session_state.input_key = 0


def initialize_counseling_system():
    try:
        # Check if required files exist
        if not os.path.exists(config.EMPLOYEE_DATA_PATH):
            st.error(
                f"Error: Employee data file not found at {config.EMPLOYEE_DATA_PATH}"
            )
            return False

        if not os.path.exists(config.QUESTIONS_PDF_PATH):
            st.error(
                f"Error: Questions PDF file not found at {config.QUESTIONS_PDF_PATH}"
            )
            return False

        # Load environment variables
        load_dotenv()
        openai_api_key = os.getenv("OPENAI_API_KEY")
        if not openai_api_key:
            st.error("Error: OPENAI_API_KEY not found in environment variables")
            return False

        # Initialize knowledge bases
        kb_manager = KnowledgeBaseManager(
            employee_data_path=config.EMPLOYEE_DATA_PATH,
            questions_pdf_path=config.QUESTIONS_PDF_PATH,
            db_uri=config.DB_URI,
        )

        # Load knowledge bases
        kb_manager.load_knowledge_bases(force_reload=False)

        # Initialize counseling agent
        counseling_agent = CounselingAgent(
            model_id=config.MODEL_ID,
            api_key=openai_api_key,
            kb_manager=kb_manager,
            system_prompt=config.CUSTOM_SYSTEM_PROMPT,
        )

        # Initialize conversation manager
        conversation_manager = ConversationManager(counseling_agent)
        st.session_state.conversation_manager = conversation_manager
        st.session_state.initialized = True

        # Start conversation and get initial question
        initial_question = conversation_manager.start_conversation()
        st.session_state.messages.append(
            {"role": "assistant", "content": initial_question}
        )

        return True
    except Exception as e:
        st.error(f"Error initializing the counseling system: {str(e)}")
        st.error(traceback.format_exc())
        return False


def main():
    try:
        st.title("🤝 Employee Counseling Assistant")

        # Initialize session state
        initialize_session_state()

        # Sidebar
        with st.sidebar:
            st.header("About")
            st.markdown(
                """
            This is an AI-powered employee counseling assistant that helps employees 
            with their professional development and workplace concerns.
            """
            )

            if st.button("Start New Session", type="primary"):
                st.session_state.messages = []
                st.session_state.initialized = False
                st.session_state.input_key += 1  # Increment key to reset input
                st.rerun()

        # Main chat interface
        if not st.session_state.initialized:
            if st.button("Initialize Counseling Session", type="primary"):
                if initialize_counseling_system():
                    st.success("Counseling session initialized successfully!")
                else:
                    st.error("Failed to initialize the counseling session.")

        # Display chat messages
        for message in st.session_state.messages:
            with st.container():
                if message["role"] == "assistant":
                    st.markdown(
                        f"""
                        <div class="chat-message assistant-message">
                            <b>Counselor:</b> {message["content"]}
                        </div>
                    """,
                        unsafe_allow_html=True,
                    )
                else:
                    st.markdown(
                        f"""
                        <div class="chat-message user-message">
                            <b>You:</b> {message["content"]}
                        </div>
                    """,
                        unsafe_allow_html=True,
                    )

        # Chat input
        if st.session_state.initialized:
            user_input = st.text_input(
                "Your response:", key=f"user_input_{st.session_state.input_key}"
            )

            if user_input:
                # Add user message to chat history
                st.session_state.messages.append(
                    {"role": "user", "content": user_input}
                )

                # Process user response
                with st.spinner("Processing your response..."):
                    try:
                        response = (
                            st.session_state.conversation_manager.handle_response(
                                user_input
                            )
                        )
                        st.session_state.messages.append(
                            {"role": "assistant", "content": response}
                        )

                        # Check if conversation is complete
                        if (
                            st.session_state.conversation_manager.is_conversation_complete()
                        ):
                            st.success("Counseling session completed!")
                            report = (
                                st.session_state.conversation_manager.generate_final_report()
                            )

                            # Save report
                            with open("employee_counseling_report.md", "w") as f:
                                f.write(report)

                            # Display report
                            st.markdown("### 📊 Counseling Session Report")
                            st.markdown(report)

                            # Download button for report
                            with open("employee_counseling_report.md", "rb") as f:
                                st.download_button(
                                    label="Download Report",
                                    data=f,
                                    file_name="employee_counseling_report.md",
                                    mime="text/markdown",
                                )
                    except Exception as e:
                        st.error(f"Error processing response: {str(e)}")
                        st.error(traceback.format_exc())
                        st.warning(
                            "Would you like to try again or start a new session?"
                        )

                # Increment input key to clear input
                st.session_state.input_key += 1
                st.rerun()

    except Exception as e:
        st.error(f"An unexpected error occurred: {str(e)}")
        st.error(traceback.format_exc())


if __name__ == "__main__":
    main()
