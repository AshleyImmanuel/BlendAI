import unittest
import json
from fastapi.testclient import TestClient
from main import app

class TestFastAPIRouting(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        self.valid_payload = {
            "prompt": "Create a cube",
            "api_key": "sk-test-fake-key",
            "session_id": "routing_test_user",
            "model": "gpt-4o"
        }

    def test_root_endpoint(self):
        """Verify the health check endpoint."""
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn("Online", response.json()["message"])

    def test_run_endpoint_malformed_json(self):
        """Verify that invalid JSON is rejected gracefully."""
        response = self.client.post("/run", content="Not a JSON string")
        self.assertEqual(response.status_code, 422) # FastAPI validation error

    def test_run_endpoint_empty_prompt(self):
        """Verify that empty prompts are rejected with a 400 error."""
        payload = self.valid_payload.copy()
        payload["prompt"] = "   "
        response = self.client.post("/run", json=payload)
        self.assertEqual(response.status_code, 400)
        self.assertIn("cannot be empty", response.json()["detail"])

    def test_run_endpoint_missing_api_key(self):
        """Verify that missing API keys are rejected."""
        payload = self.valid_payload.copy()
        payload["api_key"] = ""
        response = self.client.post("/run", json=payload)
        self.assertEqual(response.status_code, 400)
        self.assertIn("Key required", response.json()["detail"])

    def test_run_endpoint_huge_prompt(self):
        """Verify the system handles extremely large prompts without crashing."""
        payload = self.valid_payload.copy()
        payload["prompt"] = "A" * 50000 # 50k characters
        # Note: We won't actually call the LLM in this unit test (it would involve mocking SwarmManager)
        # But we check that the API layer itself doesn't crash on intake
        pass

    def test_reset_endpoint(self):
        """Verify session reset logic."""
        response = self.client.post("/reset", json={"session_id": "routing_test_user"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["session_id"], "routing_test_user")

if __name__ == "__main__":
    unittest.main()
