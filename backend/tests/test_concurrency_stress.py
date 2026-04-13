import unittest
from fastapi.testclient import TestClient
from main import app
import time

class TestConcurrencyStress(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        self.valid_payload = {
            "prompt": "Create a cube",
            "api_key": "sk-test-fake-key",
            "session_id": "concurrency_user",
            "model": "gpt-4o"
        }

    def test_rate_limiter_enforcement(self):
        """Verify that the 10-per-minute rate limit is strictly enforced."""
        results = []
        # We know the limit is 10. Let's fire 15 rapidly.
        # Note: In a real test we might mock SwarmManager to make it instant
        with unittest.mock.patch('agents.swarm_manager.SwarmManager.resolve', return_value={"code": "", "report": "OK", "new_skill": None}):
            for i in range(15):
                response = self.client.post("/run", json=self.valid_payload)
                results.append(response.status_code)

        # The first 10 should be 200
        # The remaining 5 should be 429
        success_count = results.count(200)
        limit_count = results.count(429)

        print(f"\n[STRESS] Rate Limit Results: {success_count} Successes, {limit_count} Redjections.")
        
        self.assertEqual(success_count, 10, "First 10 requests should succeed.")
        self.assertGreater(limit_count, 0, "Requests beyond the limit must be rejected with 429.")

if __name__ == "__main__":
    unittest.main()
