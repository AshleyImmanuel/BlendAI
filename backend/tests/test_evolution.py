import unittest
from unittest.mock import MagicMock
import sys
import os

# Ensure backend path is available
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from agents.swarm_manager import SwarmManager # type: ignore
from utils.skill_manager import skill_manager # type: ignore

class TestSwarmEvolution(unittest.TestCase):
    def setUp(self):
        self.session_id = "evolution_test_session"
        self.mock_client = MagicMock()
        
        # Determine paths
        self.skills_dir = skill_manager.skills_dir
        self.test_skill_name = "test_evo_skill.py"
        self.test_skill_path = os.path.join(self.skills_dir, self.test_skill_name)
        
        # Cleanup
        if os.path.exists(self.test_skill_path):
            os.remove(self.test_skill_path)

    def test_manual_skill_creation(self):
        """Verify that the ManagerAgent can manually trigger a skill save."""
        swarm = SwarmManager(api_key="fake", model="gpt-4o")
        swarm.manager.llm = self.mock_client
        swarm.planner.llm = self.mock_client
        swarm.executor.llm = self.mock_client
        swarm.critic.llm = self.mock_client
        
        # Simulate: 1. Manager says 'SAVE_AS_SKILL', 2. Planner plans, 3. Executor codes, 4. Critic OKs
        self.mock_client.completion.side_effect = [
            "Expert, SAVE_AS_SKILL: test_evo_skill", # Manager
            "1. Plan",                               # Planner
            "print('evolution')",                   # Executor
            "OK"                                     # Critic
        ]
        
        result = swarm.resolve(self.session_id, "Save this as a skill called test_evo_skill")
        self.assertEqual(result["new_skill"], "test_evo_skill.py")
        self.assertTrue(os.path.exists(self.test_skill_path))
        
        with open(self.test_skill_path, "r") as f:
            content = f.read()
            self.assertIn("print('evolution')", content)
            self.assertIn("Description:", content)

    def test_autonomous_promotion(self):
        """Verify that the CriticAgent can suggest autonomous promotion."""
        swarm = SwarmManager(api_key="fake", model="gpt-4o")
        swarm.manager.llm = self.mock_client
        swarm.planner.llm = self.mock_client
        swarm.executor.llm = self.mock_client
        swarm.critic.llm = self.mock_client
        
        auto_skill_name = "auto_masterpiece.py"
        auto_skill_path = os.path.join(self.skills_dir, auto_skill_name)
        if os.path.exists(auto_skill_path): os.remove(auto_skill_path)

        # Simulate: 1. Manager Activate, 2. Planner, 3. Executor, 4. Critic Suggests Promotion
        self.mock_client.completion.side_effect = [
            "Executor",                             # Manager
            "1. Plan",                              # Planner
            "print('masterpiece')",                 # Executor
            "OK [PROMOTABLE: auto_masterpiece, Professional code]" # Critic
        ]
        
        result = swarm.resolve(self.session_id, "Something brilliant")
        self.assertEqual(result["new_skill"], "auto_masterpiece.py")
        self.assertTrue(os.path.exists(auto_skill_path))
        
        # Cleanup
        os.remove(auto_skill_path)

    def tearDown(self):
        if os.path.exists(self.test_skill_path):
            os.remove(self.test_skill_path)

if __name__ == "__main__":
    unittest.main()
