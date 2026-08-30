import unittest
from fastapi.testclient import TestClient # type: ignore
import sys
import os

# Ensure backend path is available
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from main import app # type: ignore

client = TestClient(app)

class TestBlendAI_API(unittest.TestCase):
    def test_root_endpoint(self):
        """Verify the 'Online' heartbeat."""
        response = client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["message"], "BlendAI Swarm is Online")

    def test_missing_api_key(self):
        """Verify that the API rejects requests without a key with a clear toast-ready error."""
        response = client.post("/run", json={
            "prompt": "Create a cube",
            "api_key": "",
            "session_id": "test"
        })
        self.assertEqual(response.status_code, 400)
        self.assertIn("API Key required", response.json()["detail"])

    def test_rate_limiting(self):
        """Verify that the budget-protection rate limiter triggers correctly."""
        # 10 req/min limit. Let's hit it 11 times.
        payload = {
            "prompt": "Test",
            "api_key": "fake_key_123456",
            "session_id": "rate_test"
        }
        
        for _ in range(10):
            client.post("/run", json=payload)
            
        # The 11th should fail
        response = client.post("/run", json=payload)
        self.assertEqual(response.status_code, 429)
        self.assertIn("Rate limit exceeded", response.json()["detail"])

if __name__ == "__main__":
    unittest.main()
