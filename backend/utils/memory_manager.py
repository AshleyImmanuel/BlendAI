from collections import deque
from typing import Dict, List, Any, Optional

class MemoryManager:
    """
    Manages session-based conversation history for the AI agents.
    Stored in-memory (per server instance).
    """
    def __init__(self, max_history: int = 5):
        self.max_history = max_history
        # Structure: { session_id: deque([history_objects]) }
        self.sessions: Dict[str, deque] = {}

    def add_interaction(self, session_id: str, prompt: str, code: str):
        """Adds a new interaction (prompt and successfully generated code) to history."""
        if session_id not in self.sessions:
            self.sessions[session_id] = deque(maxlen=self.max_history)
        
        self.sessions[session_id].append({
            "prompt": prompt,
            "code": code
        })

    def get_history_context(self, session_id: str) -> str:
        """Formats the history into a string context for the LLM."""
        history = self.get_history(session_id)
        if not history:
            return "No previous history."
        
        context = []
        for i, item in enumerate(history):
            context.append(f"Turn {i+1}:\nUser Prompt: {item['prompt']}\nGenerated Code: {item['code']}\n")
        
        return "\n".join(context)

    def get_history(self, session_id: str) -> List[Dict[str, Any]]:
        """Returns the raw history list for a session."""
        if session_id not in self.sessions:
            return []
        return list(self.sessions[session_id])

    def clear_session(self, session_id: str):
        """Clears memory for a specific session."""
        if session_id in self.sessions:
            self.sessions[session_id].clear()

# Global singleton for the backend
memory_db = MemoryManager()
