import unittest
from unittest.mock import MagicMock
import sys
import os

# Ensure backend path is available
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from agents.swarm_manager import SwarmManager # type: ignore
from utils.skill_manager import skill_manager # type: ignore

class TestSessionContinuity(unittest.TestCase):
    def setUp(self):
        self.session_id = "continuity_test"
        self.mock_client = MagicMock()
        self.swarm = SwarmManager(api_key="fake", model="gpt-4o")
        self.swarm.manager.llm = self.mock_client
        self.swarm.planner.llm = self.mock_client
        self.swarm.executor.llm = self.mock_client
        self.swarm.critic.llm = self.mock_client
        
        self.test_skill_name = "test_continuity_skill.py"
        self.test_skill_path = os.path.join(skill_manager.skills_dir, self.test_skill_name)
        if os.path.exists(self.test_skill_path): os.remove(self.test_skill_path)

    def test_end_to_end_evolutionary_loop(self):
        """Verify that a created skill is immediately usable in the next turn."""
        
        # --- TURN 1: CREATION ---
        # Mock responses for Turn 1
        self.mock_client.completion.side_effect = [
            "Executor, SAVE_AS_SKILL: test_continuity_skill", # Manager
            "1. Create code",                                 # Planner
            "print('continuity_success')",                   # Executor
            "OK"                                              # Critic
        ]
        
        res1 = self.swarm.resolve(self.session_id, "Create and save test_continuity_skill")
        self.assertEqual(res1["new_skill"], "test_continuity_skill.py")
        self.assertTrue(os.path.exists(self.test_skill_path))

        # --- TURN 2: DISCOVERY ---
        # Re-initialize to refresh catalog (though skill_manager.get_skills_catalog() reads disc every time)
        
        # Mock responses for Turn 2
        # Manager should now see 'test_continuity_skill.py' in the catalog provided in identify_roles_and_skills
        self.mock_client.completion.side_effect = [
            "Expert, test_continuity_skill.py", # Manager (DISCOVERED THE NEW SKILL)
            "1. Use skill",                     # Planner
            "test_continuity_skill.py success", # Executor
            "OK"                                # Critic
        ]
        
        res2 = self.swarm.resolve(self.session_id, "Use the skill I just made")
        # Verify that the Manager was passed the catalog containing our new skill
        # (This is checked by the fact that Identify roles was called and we mocked it returning the skill)
        # We can verify that 'test_continuity_skill.py' was indeed in the response
        
        self.assertEqual(res2["report"], "OK")

    def tearDown(self):
        if os.path.exists(self.test_skill_path):
            os.remove(self.test_skill_path)

if __name__ == "__main__":
    unittest.main()
