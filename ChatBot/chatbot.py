import os
import traceback
from fastapi import FastAPI, HTTPException, BackgroundTasks, APIRouter
from pydantic import BaseModel
from . import config
from pathlib import Path
import requests
import json
from typing import List, Optional
from dotenv import load_dotenv
from datetime import datetime, timezone
from google.cloud import storage

from .daily_report import SummarizerAgent

# Load environment variables
load_dotenv()

try:
    from .knowledge_base import KnowledgeBaseManager
except TypeError:
    print("Using simple knowledge base manager without chunking parameters...")
    from .knowledge_base import KnowledgeBaseManager

from .counseling_agent import CounselingAgent
from .conversation_manager import ConversationManager
from .summary_agent import SummarizerAgent, Message, SenderType

router = APIRouter()

# Store active sessions
active_sessions = {}

# Initialize components
summarizer_agent = SummarizerAgent(model="gemini-1.5-flash")

# Define reports directory paths
REPORTS_DIR = Path(__file__).parent.parent / "emp_reports"
COUNSELLING_REPORTS_DIR = Path(__file__).parent.parent / "emp_counselling_reports"

# Ensure the directories exist
REPORTS_DIR.mkdir(exist_ok=True)
COUNSELLING_REPORTS_DIR.mkdir(exist_ok=True)

# Backend API URL
BACKEND_API_URL = os.getenv("BACKEND_API_URL", "http://localhost:8000")
GCS_BUCKET_NAME = os.getenv("GCS_BUCKET_NAME")
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "key.json"

class SessionRequest(BaseModel):
    session_id: str
    chain_id: str
    context: Optional[str] = None

class SessionResponse(BaseModel):
    session_id: str
    message: str

class MessageRequest(BaseModel):
    session_id: str
    message: str
    chain_id: str = None

class MessageResponse(BaseModel):
    message: str

class EndSessionRequest(BaseModel):
    session_id: str
    chain_id: str
    current_context: Optional[str] = None

class EndSessionResponse(BaseModel):
    updated_context: str
    message: str

class ChainContextUpdateRequest(BaseModel):
    chain_id: str
    context: str

class ChainCompletionRequest(BaseModel):
    chain_id: str
    reason: str

class ChainEscalationRequest(BaseModel):
    chain_id: str
    reason: str

def initialize_session(chain_id: str, session_id: str, background_tasks: BackgroundTasks, context: Optional[str] = None):
    try:
        # Check if required files exist
        questions_pdf_path = Path(__file__).parent.parent / "ChatBot" / config.QUESTIONS_PDF_PATH
        if not os.path.exists(questions_pdf_path):
            raise Exception(f"Error: Questions PDF file not found at {questions_pdf_path}")
        
        # Check if employee report exists
        report_path = REPORTS_DIR / f"{chain_id}_report.txt"
        print(f"Looking for report at: {report_path}")
        if not report_path.exists():
            raise Exception(f"Error: Employee report not found for ID {chain_id}")

        print(f"Employee report found at {report_path}")
        
        # Initialize knowledge bases
        print("Setting up knowledge bases...")
        kb_manager = KnowledgeBaseManager(
            employee_data_path=str(report_path),
            questions_pdf_path=str(questions_pdf_path),
            db_uri=f"tmp/counselling_db_{chain_id}"
        )
        
        # Load knowledge bases - will skip if already loaded
        kb_manager.load_knowledge_bases(force_reload=False)
        
        # Initialize counseling agent with context
        print("Initializing counseling agent...")
        
        # Prepare context for the counseling agent
        agent_context = context if context else ""
        
        counseling_agent = CounselingAgent(
            model_id=config.MODEL_ID,
            kb_manager=kb_manager,
            system_prompt=config.CUSTOM_SYSTEM_PROMPT,
            context=agent_context,
            report_file_path=report_path
        )
        
        # Initialize conversation manager 
        conversation_manager = ConversationManager(counseling_agent)
        
        # Start the conversation
        first_question = conversation_manager.start_conversation()
        
        # Store the session
        active_sessions[session_id] = {
            "conversation_manager": conversation_manager,
            "chain_id": chain_id,
            "complete": False,
            "escalated": False,
            "context": context,
            "messages": [],
            "start_time": datetime.now(),
            "end_time": None
        }
        
        # Add the first question to messages
        active_sessions[session_id]["messages"].append({
            "sender": "bot",
            "text": first_question,
            "timestamp": datetime.now(timezone.utc)
        })
        
        return first_question
    except Exception as e:
        print(f"Error in initialize_session: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))

def save_counselling_report_to_gcs(employee_id: str, session_id: str, report: str, escalated: bool):
    """Save the counseling report to a Google Cloud Storage bucket."""
    try:
        report_type = "escalated" if escalated else "standard"
        filename = f"{employee_id}_{session_id}_{report_type}.md"

        # Compose the content of the report
        content = (
            f"# Counseling Report for Employee {employee_id}\n\n"
            f"Session ID: {session_id}\n"
            f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            f"Report Type: {report_type.title()}\n\n"
            f"---\n\n"
            f"{report}"
        )

        # Initialize Google Cloud Storage client
        storage_client = storage.Client()
        bucket = storage_client.bucket(GCS_BUCKET_NAME)
        blob = bucket.blob(filename)

        # Upload content as a string
        blob.upload_from_string(content, content_type="text/markdown")

        print(f"Report uploaded to GCS as {filename}")
        return f"gs://{GCS_BUCKET_NAME}/{filename}"

    except Exception as e:
        print(f"Error uploading report to GCS: {str(e)}")
        print(traceback.format_exc())
        return None

def save_session_report_to_gcs(chain_id: str, session_id: str, report: str):
    """Save the counseling report to a Google Cloud Storage bucket."""
    try:
        filename = f"{chain_id}_{session_id}_report.md"
        storage_client = storage.Client()
        bucket = storage_client.bucket(GCS_BUCKET_NAME)
        blob = bucket.blob(filename)
        blob.upload_from_string(report, content_type="text/markdown")
        print(f"Report uploaded to GCS as {filename}")
        return f"gs://{GCS_BUCKET_NAME}/{filename}"
    except Exception as e:
        print(f"Error uploading report to GCS: {str(e)}")
        print(traceback.format_exc())
        return None

# health check
@router.get("/")
async def health_check():
    return {"status": "ok"}

@router.post("/start_session", response_model=SessionResponse)
async def start_session(request: SessionRequest, background_tasks: BackgroundTasks):
    try:
        first_message = initialize_session(
            request.chain_id, 
            request.session_id, 
            background_tasks, 
            request.context
        )
        return {"session_id": request.session_id, "message": first_message}
    except Exception as e:
        print(f"Error in start_session: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/message", response_model=MessageResponse)
async def process_message(request: MessageRequest):
    try:
        # Check if session exists
        if request.session_id not in active_sessions:
            raise HTTPException(status_code=404, detail="Session not found")
        
        session = active_sessions[request.session_id]
        
        # Check if conversation is already complete
        if session["complete"]:
            raise HTTPException(status_code=400, detail="Conversation is already complete")
        
        # Store the user message in the session
        session["messages"].append({
            "sender": "employee",
            "text": request.message,
            "timestamp": datetime.now(timezone.utc)
        })
        
        # Process the message
        conversation_manager = session["conversation_manager"]
        next_question = conversation_manager.handle_response(request.message)
        
        # Store the bot response in the session
        session["messages"].append({
            "sender": "bot",
            "text": next_question,
            "timestamp": datetime.now(timezone.utc)
        })

        complete_the_chain = False
        escalate_the_chain = False

        
        # Check if conversation is now complete
        if conversation_manager.is_conversation_complete():
            session["complete"] = True
            session["end_time"] = datetime.now(timezone.utc)
            
            # Check if conversation is escalated
            session["escalated"] = conversation_manager.is_conversation_escalated()
            escalate_the_chain = session["escalated"]
            
            # Generate report in the background
            report = conversation_manager.generate_final_report()
            session["report"] = report
            
            # Save the report to a file
            report_path = save_counselling_report_to_gcs(
                session["chain_id"],
                request.session_id,
                report,
                session["escalated"]
            )
            session["report_file_path"] = report_path
            
            # If chain_id is provided, complete the chain
            if session.get("chain_id"):
                complete_the_chain = True
        
        # Check if conversation needs to be escalated
        if conversation_manager.is_conversation_escalated():
            session["escalated"] = True
            
            # If chain_id is provided, escalate the chain
            if session.get("chain_id"):
                complete_the_chain = True
                escalate_the_chain = True
        
        return {"message": next_question, "complete_the_chain": complete_the_chain, "escalate_the_chain": escalate_the_chain}
    except Exception as e:
        print(f"Error in process_message: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/end_session", response_model=EndSessionResponse)
async def end_session(request: EndSessionRequest):
    try:
        # Check if session exists
        if request.session_id not in active_sessions:
            raise HTTPException(status_code=404, detail="Session not found")
        
        session = active_sessions[request.session_id]
        
        # Set end time if not already set
        if not session["end_time"]:
            session["end_time"] = datetime.now()
        
        print(session)
        
        # Get all messages from the session
        messages = []
        for msg in session["messages"]:
            print(msg)
            print(msg.keys())

            messages.append(Message(
                sender_type=SenderType.EMPLOYEE if msg["sender"] == "employee" else SenderType.BOT,
                text=msg["text"],
                timestamp=msg["timestamp"]
            ))
        
        # Get the current context
        current_context = request.current_context or session.get("context", "")
        
        # Summarize the conversation
        updated_context = summarizer_agent.summarize_conversation(current_context, messages)
        
        session["complete"] = True
        session["end_time"] = datetime.now(timezone.utc)

        msgs = [
            Message(
                sender_type=SenderType.EMPLOYEE,
                text=request.message,
                timestamp=datetime.now(timezone.utc)
            ) for msg in session["messages"]
        ]
        
        report = SummarizerAgent.generate_daily_report(updated_context, msgs)

        # Save the report to a file
        report_path = save_session_report_to_gcs(
            request.chain_id,
            request.session_id,
            report
        )
        session["report_file_path"] = report_path
        
        return {
            "chain_id": request.chain_id,
            "updated_context": updated_context,
            "message": "Session ended successfully"
        }
    except Exception as e:
        print(f"Error in end_session: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/report/{session_id}")
async def get_report(session_id: str):
    try:
        # Check if session exists
        if session_id not in active_sessions:
            raise HTTPException(status_code=404, detail="Session not found")
        
        session = active_sessions[session_id]
        
        # Check if conversation is complete and report is available
        if not session["complete"]:
            raise HTTPException(status_code=400, detail="Conversation is not complete yet")
        
        if "report" not in session:
            raise HTTPException(status_code=404, detail="Report not found")
        
        # Return the report with status information
        return {
            "report": session["report"],
            "escalated": session.get("escalated", False),
            "chain_id": session["chain_id"],
            "report_type": "escalation" if session.get("escalated", False) else "standard",
            "report_file_path": session.get("report_file_path")
        }
    except Exception as e:
        print(f"Error in get_report: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/session_status/{session_id}")
async def get_session_status(session_id: str):
    try:
        # Check if session exists
        if session_id not in active_sessions:
            raise HTTPException(status_code=404, detail="Session not found")
        
        session = active_sessions[session_id]
        
        return {
            "session_id": session_id,
            "chain_id": session["chain_id"],
            "complete": session["complete"],
            "escalated": session.get("escalated", False),
            "message_count": len(session["messages"]),
            "has_report": "report" in session,
            "report_file_path": session.get("report_file_path"),
            "start_time": session.get("start_time"),
            "end_time": session.get("end_time")
        }
    except Exception as e:
        print(f"Error in get_session_status: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))