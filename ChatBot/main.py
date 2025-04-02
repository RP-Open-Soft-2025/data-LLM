import os
import uuid
import uvicorn
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import config
from pathlib import Path

# Try the updated version first, if it fails, use the simpler version
try:
    from knowledge_base import KnowledgeBaseManager
except TypeError:
    print("Using simple knowledge base manager without chunking parameters...")
    from knowledge_base import KnowledgeBaseManager

from counseling_agent import CounselingAgent
from conversation_manager import ConversationManager

app = FastAPI(
    title="Counseling Agent API",
    description="API for interacting with a counseling agent",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Store active sessions
active_sessions = {}

# Initialize components
kb_manager = None
counseling_agent = None

# Define reports directory path
REPORTS_DIR = Path(__file__).parent.parent / "emp_reports"


class SessionRequest(BaseModel):
    employee_id: str
    session_id: str


class SessionResponse(BaseModel):
    session_id: str
    message: str


class MessageRequest(BaseModel):
    session_id: str
    message: str


class MessageResponse(BaseModel):
    message: str


def setup_system(employee_id: str):
    global kb_manager, counseling_agent

    # Check if required files exist
    if not os.path.exists(config.QUESTIONS_PDF_PATH):
        raise Exception(
            f"Error: Questions PDF file not found at {config.QUESTIONS_PDF_PATH}"
        )

    # Check if employee report exists
    report_path = REPORTS_DIR / f"{employee_id}_report.txt"
    if not report_path.exists():
        raise Exception(f"Error: Employee report not found for ID {employee_id}")

    print(f"Employee report found at {report_path}")

    # Initialize knowledge bases
    print("Setting up knowledge bases...")
    kb_manager = KnowledgeBaseManager(
        employee_data_path=str(
            report_path
        ),  # Use the employee report as the knowledge base
        questions_pdf_path=config.QUESTIONS_PDF_PATH,
        db_uri=f"tmp/counselling_db_{employee_id}",  # Create unique DB for each employee
    )

    # Load knowledge bases - will skip if already loaded
    kb_manager.load_knowledge_bases(force_reload=True)

    # Initialize counseling agent
    print("Initializing counseling agent...")
    counseling_agent = CounselingAgent(
        model_id=config.MODEL_ID,
        # api_key=config.GROQ_API_KEY,
        kb_manager=kb_manager,
        system_prompt=config.CUSTOM_SYSTEM_PROMPT,
    )


def initialize_session(
    employee_id: str, session_id: str, background_tasks: BackgroundTasks
):
    # Generate a unique session ID
    # session_id = str(uuid.uuid4())

    try:
        # Setup system with employee report
        setup_system(employee_id)

        # Initialize conversation manager
        conversation_manager = ConversationManager(counseling_agent)

        # Start the conversation
        first_question = conversation_manager.start_conversation()

        # Store the session
        active_sessions[session_id] = {
            "conversation_manager": conversation_manager,
            "employee_id": employee_id,
            "complete": False,
        }

        return session_id, first_question
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.on_event("startup")
async def startup_event():
    # Create reports directory if it doesn't exist
    REPORTS_DIR.mkdir(exist_ok=True)


# health check
@app.get("/")
async def health_check():
    return {"status": "ok"}


@app.post("/start_session", response_model=SessionResponse)
async def start_session(request: SessionRequest, background_tasks: BackgroundTasks):
    session_id, first_message = initialize_session(
        request.employee_id, request.session_id, background_tasks
    )
    return {"session_id": session_id, "message": first_message}


@app.post("/message", response_model=MessageResponse)
async def process_message(request: MessageRequest):
    # Check if session exists
    if request.session_id not in active_sessions:
        raise HTTPException(status_code=404, detail="Session not found")

    session = active_sessions[request.session_id]

    # Check if conversation is already complete
    if session["complete"]:
        raise HTTPException(status_code=400, detail="Conversation is already complete")

    # Process the message
    conversation_manager = session["conversation_manager"]
    next_question = conversation_manager.handle_response(request.message)

    # Check if conversation is now complete
    if conversation_manager.is_conversation_complete():
        session["complete"] = True
        # Generate report in the background
        report = conversation_manager.generate_final_report()
        session["report"] = report

    return {"message": next_question}


@app.get("/report/{session_id}")
async def get_report(session_id: str):
    # Check if session exists
    if session_id not in active_sessions:
        raise HTTPException(status_code=404, detail="Session not found")

    session = active_sessions[session_id]

    # Check if conversation is complete and report is available
    if not session["complete"]:
        raise HTTPException(status_code=400, detail="Conversation is not complete yet")

    if "report" not in session:
        raise HTTPException(status_code=404, detail="Report not found")

    return {"report": session["report"]}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
