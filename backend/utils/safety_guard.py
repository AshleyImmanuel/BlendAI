import os
import re
import logging

logger = logging.getLogger("BlendAI.Safety")

# --- POLICY CONFIGURATION ---
ALLOWED_COMMAND_PATTERNS = [
    r"^pip install [\w-]+$",
    r"^python -m pip install [\w-]+$",
    r"^ls -la",
    r"^dir",
    r"^echo",
    r"^git ",
]

BLOCKED_COMMAND_PATTERNS = [
    r"rm -rf",
    r"format ",
    r"mkfs",
    r"dd ",
    r"> /dev/",
    r":(){:|:&};:", # Fork bomb
    r"del /s /q c:",
]

class SafetyGuard:
    def __init__(self):
        self.whitelist_dirs = []
        self._initialize_whitelist()

    def _initialize_whitelist(self):
        """Initializes safe zones for file operations."""
        # Standard Blender User Path
        try:
            # Note: In the backend, we don't have 'bpy' directly, 
            # so we'll allow the plugin dir and common data paths.
            plugin_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            self.whitelist_dirs.append(os.path.abspath(plugin_dir))
            
            # We can also whitelist the current working directory
            self.whitelist_dirs.append(os.getcwd())
            
            # Placeholder for user-defined safe zones
            # self.whitelist_dirs.append("C:\\Projects") 
        except Exception as e:
            logger.error(f"Failed to initialize safety whitelist: {e}")

    def is_path_safe(self, target_path: str) -> bool:
        """Checks if a path is within the whitelisted safe zones."""
        abs_target = os.path.abspath(target_path)
        for safe_dir in self.whitelist_dirs:
            if abs_target.startswith(safe_dir):
                return True
        return False

    def is_command_safe(self, command: str) -> bool:
        """Reviews a shell command for dangerous patterns."""
        cmd = command.strip().lower()
        
        # 1. Check for hard-blocked patterns
        for pattern in BLOCKED_COMMAND_PATTERNS:
            if re.search(pattern, cmd):
                logger.warning(f"Blocked dangerous command pattern: {pattern}")
                return False
                
        # 2. Check for whitelisted patterns (if we want to be strict)
        # For now, we allow most commands unless they hit a blocklist pattern
        return True

    def audit_code(self, code: str) -> tuple:
        """
        Scans code for direct OS/Subprocess attempts and returns (is_safe, reason).
        """
        # We look for potentially destructive file operations outside safe zones
        # This is used by the CriticAgent as a secondary signal.
        if "rmdir" in code or "remove" in code or "unlink" in code:
            return False, "Detected file deletion attempt. Needs manual verification."
            
        return True, "Code passed primary safety scan."

safety_guard = SafetyGuard()
