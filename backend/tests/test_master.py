import unittest
from unittest.mock import MagicMock
import sys
import os

# Ensure backend path is available
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from agents.swarm_manager import SwarmManager # type: ignore
from utils.persistent_memory import persistent_memory # type: ignore
from utils.skill_manager import skill_manager # type: ignore

class TestBlendAI_Master(unittest.TestCase):
    def setUp(self):
        self.session_id = "master_test_session"
        self.mock_client = MagicMock()
        
        # Ensure we are testing against the actual project structure
        self.skills_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "skills"))
        
        # Clean up existing test memory
        persistent_memory.clear_session(self.session_id)

    def test_end_to_end_flow(self):
        """Verify the full lifecycle from Skill Discovery to Memory Persistence."""
        
        # 1. Skill Discovery Check (Using the real catalog method)
        catalog = skill_manager.get_skills_catalog()
        self.assertNotIn("empty", catalog.lower(), "The skill library appears empty in the audit!")
        print(f"[Master Test] Verified Skill Catalog Discovery")

        # 2. Swarm Logic with Memory
        swarm = SwarmManager(api_key="fake", model="gpt-4o")
        # Inject mocks into internal agents
        swarm.manager.llm = self.mock_client
        swarm.planner.llm = self.mock_client
        swarm.executor.llm = self.mock_client
        swarm.critic.llm = self.mock_client

        # Mock a successful interaction
        self.mock_client.completion.side_effect = [
            "Executor, scene_utils.py", # 1. Manager (Role + Skill)
            "1. Run master test",       # 2. Planner
            "print('GOLD MASTER')",      # 3. Executor
            "OK"                         # 4. Critic
        ]

        # 3. Resolve Mission
        result = swarm.resolve(self.session_id, "Do a master test")
        code = result["code"]
        report = result["report"]
        self.assertEqual(code, "print('GOLD MASTER')")
        print("[Master Test] Verified Swarm Logic & Skill Injection")

        # 4. Persistence Check
        # Check if the session file was created correctly
        path = persistent_memory._get_file_path(self.session_id)
        self.assertTrue(os.path.exists(path), "Memory file was not created!")
        
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
            self.assertIn("GOLD MASTER", content)
        print("[Master Test] Verified Persistent Memory Integrity")

    def tearDown(self):
        # Cleanup
        persistent_memory.clear_session(self.session_id)

if __name__ == "__main__":
    unittest.main()
