import json
from datetime import datetime
from typing import List, Dict, Any

def format_conversation_for_prompt(conversation_history: List[Dict[str, Any]], max_entries: int = 10) -> str:
    """Format the conversation history into a readable format for prompts, limiting the size."""
    # If the conversation is too long, only use the most recent entries
    if len(conversation_history) > max_entries:
        conversation_history = conversation_history[-max_entries:]
    
    formatted = ""
    for entry in conversation_history:
        sender = "Counselor" if entry["sender_type"] == "bot" else "Employee"
        formatted += f"{sender}: {entry['message']}\n\n"
    
    return formatted

def create_session_summary(report: str, conversation_history: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Create a session summary with report and conversation history."""
    # Get session date from the first message or use current date
    session_date = None
    if conversation_history and len(conversation_history) > 0:
        try:
            session_date = conversation_history[0]["timestamp"]
        except (KeyError, IndexError):
            pass
    
    if not session_date:
        session_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    summary = {
        "report": report,
        "conversation_history": conversation_history,
        "session_metadata": {
            "total_questions": sum(1 for entry in conversation_history if entry.get("sender_type") == "bot"),
            "total_responses": sum(1 for entry in conversation_history if entry.get("sender_type") == "user"),
            "session_date": session_date,
        }
    }
    
    return summary

def save_session_summary(summary: Dict[str, Any], file_path: str) -> None:
    """Save session summary to a JSON file."""
    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(summary, file, indent=2)


# Questions.pdf    
# employee_report.txt    