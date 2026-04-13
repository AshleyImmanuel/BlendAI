import unittest
from unittest.mock import MagicMock, patch
from agents.swarm_manager import SwarmManager

class TestAgentRobustness(unittest.TestCase):
    def setUp(self):
        self.swarm = SwarmManager(api_key="sk-fake", model="gpt-4o")

    def test_manager_agent_failure_handling(self):
        """Verify that a manager crash doesn't halt the system's error reporting."""
        with patch.object(self.swarm.manager, 'identify_roles_and_skills', side_effect=Exception("API Connection Lost")):
            with patch.object(self.swarm.planner, 'plan', return_value="Fail Plan"):
                with patch.object(self.swarm.executor, 'execute', return_value="print('Fail')"):
                    with patch.object(self.swarm.critic, 'review', return_value="OK"):
                        result = self.swarm.resolve("robust_user", "Create a sphere")
                        self.assertIn("code", result)
                self.assertIsNotNone(result["code"])

    def test_critic_security_blockade_robustness(self):
        """Verify that a SECURITY_ALERT response from the critic is handled with max priority."""
        with patch.object(self.swarm.manager, 'identify_roles_and_skills', return_value=([], [])):
            with patch.object(self.swarm.planner, 'plan', return_value="Plan"):
                with patch.object(self.swarm.executor, 'execute', return_value="print('Danger')"):
                    with patch.object(self.swarm.critic, 'review', return_value="[SECURITY_ALERT] Detected unauthorized module access."):
                        result = self.swarm.resolve("robust_user", "Run system command")
                        self.assertIn("# SECURITY ERROR", result["code"])
                        self.assertIn("SECURITY_ALERT", result["report"])

    def test_error_redaction_robustness(self):
        """Verify that the SwarmManager or Main API redacts keys even in deep exceptions."""
        from main import run_ai, RunRequest
        request = RunRequest(prompt="test", api_key="SUPER_SECRET_KEY_123", session_id="test_user")
        
        with patch('agents.swarm_manager.SwarmManager.resolve', side_effect=Exception("Failed with key: SUPER_SECRET_KEY_123")):
            try:
                run_ai(request)
            except Exception as e:
                # The exception raised by the FastAPI endpoint should have redacted the key
                self.assertNotIn("SUPER_SECRET_KEY_123", str(e))
                self.assertIn("redacted", str(e).lower())

if __name__ == "__main__":
    unittest.main()
