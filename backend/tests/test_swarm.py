import unittest
from unittest.mock import MagicMock
import sys
import os

# Ensure backend path is available
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from agents.swarm_manager import SwarmManager # type: ignore
from agents.specialized_agents import ManagerAgent, CriticAgent # type: ignore

class TestSwarmCore(unittest.TestCase):
    def setUp(self):
        # Initialize agents with dummy strings
        self.manager = ManagerAgent(api_key="fake", model="gpt-4o")
        self.critic = CriticAgent(api_key="fake", model="gpt-4o")
        
        # Manually overwrite the llm with a mock for testing logic
        self.mock_client = MagicMock()
        self.manager.llm = self.mock_client
        self.critic.llm = self.mock_client

    def test_manager_identifying(self):
        """Verify that the ManagerAgent identifies specialists and skills correctly."""
        self.mock_client.completion.return_value = "MaterialExpert, scene_utils.py"
        roles, skills = self.manager.identify_roles_and_skills("Make a red glass material", "scene_utils.py")
        self.assertIn("MaterialExpert", roles)
        self.assertIn("scene_utils.py", skills)

    def test_critic_security_block(self):
        """Verify that the CriticAgent blocks dangerous system code."""
        # Note: In the real implementation, the Critic uses LLM logic to flag things.
        # Here we mock the LLM's 'Security' detection.
        self.mock_client.completion.return_value = "SECURITY_ALERT: Code contains OS module."
        feedback = self.critic.review("Create a cube", "import os\nos.system('echo hacked')")
        self.assertIn("SECURITY_ALERT", feedback)

    def test_swarm_iteration_lock(self):
        """Verify that the SwarmManager respects its internal feedback loop logic."""
        swarm = SwarmManager(api_key="fake", model="gpt-4o")
        # Ensure it doesn't try to make real API calls
        swarm.manager.llm = self.mock_client
        swarm.planner.llm = self.mock_client
        swarm.executor.llm = self.mock_client
        swarm.critic.llm = self.mock_client
        
        # Simulate a loop: 1. Manager -> 2. Planner -> 3. Executor -> 4. Critic (Fix) -> 5. Executor (Success)
        self.mock_client.completion.side_effect = [
            "Executor",              # 1. Manager
            "1. Run code",          # 2. Planner
            "print('error')",        # 3. Executor (1st attempt)
            "Fix the print line",    # 4. Critic (Found bug)
            "print('success')",      # 5. Executor (2nd attempt)
            "OK"                     # 6. Critic (Approval)
        ]
        
        result = swarm.resolve("test_session", "Hello")
        code = result["code"]
        critic_report = result["report"]
        self.assertEqual(code, "print('success')")

if __name__ == "__main__":
    unittest.main()
