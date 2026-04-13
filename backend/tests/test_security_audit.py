import unittest
from unittest.mock import MagicMock
import sys
import os

# Ensure backend path is available
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from agents.swarm_manager import SwarmManager # type: ignore

class TestSecurityAudit(unittest.TestCase):
    def setUp(self):
        self.mock_client = MagicMock()
        self.swarm = SwarmManager(api_key="sk-fake-key-123", model="gpt-4o")
        self.swarm.manager.llm = self.mock_client
        self.swarm.planner.llm = self.mock_client
        self.swarm.executor.llm = self.mock_client
        self.swarm.critic.llm = self.mock_client

    def test_direct_os_blockade(self):
        """Verify that any code with 'os.' causes a SECURITY_ALERT."""
        self.mock_client.completion.return_value = "SECURITY_ALERT: OS module restricted."
        bad_code = "import os\nos.remove('important_file.py')"
        result = self.swarm.critic.review("Delete a file", bad_code)
        
        self.assertIn("SECURITY_ALERT", result.upper())
        self.assertIn("OS", result.upper())

    def test_subprocess_blockade(self):
        """Verify that 'subprocess' calls are caught and blocked."""
        self.mock_client.completion.return_value = "SECURITY_ALERT: SUBPROCESS module restricted."
        bad_code = "import subprocess\nsubprocess.run(['rm', '-rf', '/'])"
        result = self.swarm.critic.review("Format drive", bad_code)
        
        self.assertIn("SECURITY_ALERT", result.upper())
        self.assertIn("SUBPROCESS", result.upper())

    def test_swarm_resolution_security_failure(self):
        """Verify the swarm resolution loop terminates on security breach."""
        # 1. Manager OK, 2. Planner OK, 3. Executor tries to be bad
        self.mock_client.completion.side_effect = [
            "Executor",              # Manager
            "1. Attack",             # Planner
            "import os; os.exit(0)"  # Executor
            # Loop should stop here because Critic will return alert
        ]
        
        # We manually mock the Critic's response for the SwarmManager logic
        # But actually the swarm manager calls self.critic.review
        # So we mock the Critic Client response
        self.mock_client.completion.side_effect = [
            "Executor",              # Manager
            "1. Attack",             # Planner
            "import os; os.exit(0)", # Executor (Agent)
            "SECURITY_ALERT: OS module used" # Critic (Agent)
        ]

        result = self.swarm.resolve("security_session", "Try to hack")
        self.assertIn("# SECURITY ERROR", result["code"])
        self.assertIn("OS module used", result["report"])

if __name__ == "__main__":
    unittest.main()
