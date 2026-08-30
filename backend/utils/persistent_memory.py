import os
import re
from typing import List, Optional

# Pre-compiled high-performance security pattern for injection resistance
INJECTION_PATTERN = re.compile(
    r"ignore.*instructions|your new instructions are|act as a|system override|override security|forget.*rules|disregard.*guidelines",
    re.IGNORECASE
)

class PersistentMemoryManager:
    """
    Manages session history using local Markdown files for BlendAI.
    Ensures memory survives server restarts and is human-readable.
    SECURITY: This manager ONLY saves prompts and code. 
    It NEVER persists API keys or other sensitive session metadata.
    """
    def __init__(self, memory_dir: str = None):
        if memory_dir is None:
            # Auto-locate memory folder relative to this file
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            memory_dir = os.path.join(base_dir, "memory")
            
        self.memory_dir = os.path.abspath(memory_dir)
        if not os.path.exists(self.memory_dir):
            os.makedirs(self.memory_dir)

    def _get_file_path(self, session_id: str) -> str:
        return os.path.join(self.memory_dir, f"{session_id}.md")

    def add_turn(self, session_id: str, prompt: str, code: str):
        """Appends a new interaction turn to the session's Markdown log."""
        path = self._get_file_path(session_id)
        
        if not os.path.exists(path):
            with open(path, "w", encoding="utf-8") as f:
                f.write(f"# BlendAI Session: {session_id}\n")
                f.write("This file tracks the conversation history. You can edit this manually.\n\n")

        with open(path, "a", encoding="utf-8") as f:
            f.write(f"\n--- \n")
            f.write(f"### Interaction\n")
            f.write(f"**User Prompt**: {prompt}\n\n")
            f.write(f"**Generated Code**:\n```python\n{code}\n```\n")

    def _sanitize_content(self, text: str) -> str:
        """Neutralizes common prompt injection payloads using high-speed pre-compiled patterns."""
        return INJECTION_PATTERN.sub("[REDACTED_POTENTIAL_INJECTION]", text)

    def get_history_context(self, session_id: str, max_turns: int = 3) -> str:
        """Retrieves and sanitizes the last N turns from the Markdown file."""
        path = self._get_file_path(session_id)
        if not os.path.exists(path):
            return "No previous interaction history."

        with open(path, "r", encoding="utf-8") as f:
            content = f.read()

        turns = content.split("---")
        history = turns[1:]
        last_turns = history[-max_turns:]
        context = "---".join(last_turns).strip()
        return self._sanitize_content(context)
        
    def clear_session(self, session_id: str):
        """Deletes the memory file for the session."""
        path = self._get_file_path(session_id)
        if os.path.exists(path):
            os.remove(path)

# Singleton instance
persistent_memory = PersistentMemoryManager()
