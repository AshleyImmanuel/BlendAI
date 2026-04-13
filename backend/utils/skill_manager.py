import os
import re

# Pre-compiled high-performance security pattern for injection resistance
INJECTION_PATTERN = re.compile(
    r"ignore.*instructions|your new instructions are|act as a|system override|override security|forget.*rules|disregard.*guidelines",
    re.IGNORECASE
)

class SkillManager:
    """
    Handles discovery and retrieval of specialized Blender skills.
    Ensures that the AI team knows which 'tools' it has in its library.
    """
    def __init__(self, skills_dir: str = None):
        if skills_dir is None:
            # Auto-locate skills folder relative to this file
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            skills_dir = os.path.join(base_dir, "skills")
            
        self.skills_dir = os.path.abspath(skills_dir)
        if not os.path.exists(self.skills_dir):
            os.makedirs(self.skills_dir)
            
        # Optimization: Internal Catalog Cache
        self._catalog_cache = ""
        self._last_mtime = 0.0

    def get_skills_catalog(self) -> str:
        """Returns a cached list of available skills and their descriptions."""
        try:
            current_mtime = os.path.getmtime(self.skills_dir)
            if self._catalog_cache and current_mtime <= self._last_mtime:
                return self._catalog_cache
        except OSError:
            return "The skill library is currently inaccessible."

        catalog = []
        for filename in os.listdir(self.skills_dir):
            if filename.endswith(".py") or filename.endswith(".txt"):
                path = os.path.join(self.skills_dir, filename)
                try:
                    with open(path, "r", encoding="utf-8") as f:
                        content = f.read()
                        description = "No description provided."
                        for line in content.split("\n"):
                            if "Description:" in line:
                                description = line.split("Description:")[1].strip()
                                break
                        catalog.append(f"- {filename}: {description}")
                except Exception: continue
        
        self._catalog_cache = "\n".join(catalog) if catalog else "The skill library is currently empty."
        self._last_mtime = current_mtime
        return self._catalog_cache

    def _sanitize_content(self, content: str) -> str:
        """Neutralizes common prompt injection payloads using high-speed pre-compiled patterns."""
        return INJECTION_PATTERN.sub("[REDACTED_POTENTIAL_INJECTION]", content)

    def get_skill_code(self, filename: str) -> str:
        """Retrieves and sanitizes the actual code/snippet from a skill file."""
        path = os.path.join(self.skills_dir, filename)
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
                return self._sanitize_content(content)
        return f"# Error: Skill {filename} not found."

    def save_skill(self, filename: str, code: str, description: str) -> str:
        """
        Saves a new skill to the library.
        Handles versioning if the filename already exists.
        Returns the final filename used.
        """
        # Clean filename core
        filename = filename.strip().replace(" ", "_").lower()
        
        # Extension handling
        if filename.endswith(".py"):
            base_name = filename[:-3]
        else:
            base_name = filename
            
        filename = base_name + ".py"
        target_path = os.path.join(self.skills_dir, filename)
        
        # Versioning logic
        counter = 1
        while os.path.exists(target_path):
            counter += 1
            filename = f"{base_name}_v{counter}.py"
            target_path = os.path.join(self.skills_dir, filename)
            
        # Write with professional header
        with open(target_path, "w", encoding="utf-8") as f:
            f.write(f"# Description: {description}\n")
            f.write(f"# Created autonomously by BlendAI Swarm\n\n")
            f.write(code)
            
        return filename

# Singleton instance
skill_manager = SkillManager()
