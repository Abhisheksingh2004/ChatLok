import json
from datetime import datetime
from typing import List, Dict, Any, Optional

class ChatMemory:
    def __init__(self, max_history_length: int = 10):
        self.max_history_length = max_history_length
        self.conversations = {}
    
    def add_message(self, session_id: str, role: str, content: str, metadata: Optional[Dict] = None):
        """Add a message to the chat history"""
        if session_id not in self.conversations:
            self.conversations[session_id] = []
        
        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata or {}
        }
        
        self.conversations[session_id].append(message)
        
        # Keep only the last max_history_length messages
        if len(self.conversations[session_id]) > self.max_history_length:
            self.conversations[session_id] = self.conversations[session_id][-self.max_history_length:]
    
    def get_conversation_history(self, session_id: str) -> List[Dict]:
        """Get the conversation history for a session"""
        return self.conversations.get(session_id, [])
    
    def get_context_for_llm(self, session_id: str, max_messages: int = 6) -> List[Dict]:
        """Get formatted conversation history for LLM context"""
        history = self.conversations.get(session_id, [])
        # Return the last max_messages messages
        recent_history = history[-max_messages:] if len(history) > max_messages else history
        
        # Format for LLM (remove timestamps and metadata)
        formatted_history = []
        for msg in recent_history:
            formatted_history.append({
                "role": msg["role"],
                "content": msg["content"]
            })
        
        return formatted_history
    
    def clear_session(self, session_id: str):
        """Clear the conversation history for a session"""
        if session_id in self.conversations:
            del self.conversations[session_id]
    
    def get_session_summary(self, session_id: str) -> Dict:
        """Get a summary of the session"""
        history = self.conversations.get(session_id, [])
        return {
            "session_id": session_id,
            "message_count": len(history),
            "first_message": history[0]["timestamp"] if history else None,
            "last_message": history[-1]["timestamp"] if history else None
        }
    
    def export_conversation(self, session_id: str) -> str:
        """Export conversation as JSON string"""
        return json.dumps(self.conversations.get(session_id, []), indent=2)

# Global chat memory instance
chat_memory = ChatMemory()
