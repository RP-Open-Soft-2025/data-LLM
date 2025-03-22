from datetime import datetime
from typing import List, Dict, Any
import json

class ConversationTracker:
    def __init__(self):
        """Initialize the conversation tracker."""
        self.conversation_history = []
        self.context = ""
    
    def add_message(self, sender_type: str, message: str) -> None:
        """Add a message to the conversation history."""
        timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        
        message_entry = {
            "timestamp": timestamp,
            "sender_type": sender_type,  # "bot" or "user"
            "message": message
        }
        
        self.conversation_history.append(message_entry)
    
    def update_context(self) -> None:
        """Update the context based on the last question-answer pair."""
        if len(self.conversation_history) < 2:
            return
        
        # Get the last bot question and user response
        last_messages = self.conversation_history[-2:]
        
        if last_messages[0]["sender_type"] == "bot" and last_messages[1]["sender_type"] == "user":
            question = last_messages[0]["message"]
            answer = last_messages[1]["message"]
            
            # Generate a context that's within 50 words
            combined = f"Q: {question} A: {answer}"
                
            self.context = combined
    
    def get_conversation_history(self) -> List[Dict[str, Any]]:
        """Get the entire conversation history."""
        return self.conversation_history
    
    def get_context(self) -> str:
        """Get the current context."""
        return self.context
    
    def save_conversation(self, file_path: str) -> None:
        """Save the conversation history to a JSON file."""
        with open(file_path, "w", encoding="utf-8") as file:
            json.dump(self.conversation_history, file, indent=2)
    
    def get_all_qa_pairs(self) -> List[Dict[str, Any]]:
        """Get all question-answer pairs for analysis."""
        qa_pairs = []
        
        for i in range(0, len(self.conversation_history) - 1, 2):
            if i + 1 < len(self.conversation_history):
                if self.conversation_history[i]["sender_type"] == "bot" and \
                   self.conversation_history[i+1]["sender_type"] == "user":
                    qa_pairs.append({
                        "question": self.conversation_history[i]["message"],
                        "answer": self.conversation_history[i+1]["message"],
                        "timestamp": self.conversation_history[i+1]["timestamp"]
                    })
        
        return qa_pairs