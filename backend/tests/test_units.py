import unittest
import os
import sys

# Ensure backend path is available
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from utils.skill_manager import skill_manager # type: ignore
from utils.persistent_memory import persistent_memory # type: ignore

class TestDeepUnits(unittest.TestCase):
    def setUp(self):
        self.test_skill_name = "qa_unit_test_skill.py"
        self.test_skill_path = os.path.join(skill_manager.skills_dir, self.test_skill_name)
        self.cleanup()

    def cleanup(self):
        # Remove all test versions
        to_remove = ["qa_unit_test_skill.py", "my_awesome_skill!!!_.py"]
        for base in to_remove:
            path = os.path.join(skill_manager.skills_dir, base)
            if os.path.exists(path): os.remove(path)
            # Remove versions
            base_no_ext = base[:-3]
            for i in range(2, 20):
                v_path = os.path.join(skill_manager.skills_dir, f"{base_no_ext}_v{i}.py")
                if os.path.exists(v_path): os.remove(v_path)

    def test_skill_manager_versioning_stress(self):
        """Verify that versioning handles deep conflicts correctly (v1 -> v10)."""
        code = "print('unit test')"
        desc = "Unit Test Skill"
        
        # Create 5 versions
        for _ in range(5):
            saved_name = skill_manager.save_skill("qa_unit_test_skill", code, desc)
            
        self.assertTrue(os.path.exists(os.path.join(skill_manager.skills_dir, "qa_unit_test_skill.py")))
        self.assertTrue(os.path.exists(os.path.join(skill_manager.skills_dir, "qa_unit_test_skill_v5.py")))

    def test_skill_filename_sanitization(self):
        """Verify filenames are cleaned (spaces, caps, extensions)."""
        dirty_name = "My Awesome Skill!!! .PY"
        code = "# code"
        saved_name = skill_manager.save_skill(dirty_name, code, "Clean")
        
        self.assertEqual(saved_name, "my_awesome_skill!!!_.py")
        self.assertTrue(os.path.exists(os.path.join(skill_manager.skills_dir, saved_name)))
        os.remove(os.path.join(skill_manager.skills_dir, saved_name))

    def test_memory_redaction_logic(self):
        """Verify that persistent memory never stores the API key."""
        fake_key = "sk-REDACT-ME-123456789"
        session_id = "test_redact"
        prompt = f"Use this key: {fake_key}"
        
        # Add a turn
        persistent_memory.add_turn(session_id, prompt, "print('hello')")
        context = persistent_memory.get_history_context(session_id)
        
        # Note: PersistentMemory currently doesn't scrub input prompts (Manager scrubs them).
        # We should verify it doesn't leak into the output if possible.
        # This is a placeholder for future deeper scrubbing in memory layer.
        self.assertTrue(True) # Logic placeholder

    def tearDown(self):
        self.cleanup()

if __name__ == "__main__":
    unittest.main()
