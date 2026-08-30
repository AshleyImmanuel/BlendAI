import requests
import json
import os

def test_swarm_e2e():
    """
    A simple end-to-end test script for the BlendAI Swarm.
    Ensures the backend, manager, and memory are all communicating.
    """
    url = "http://localhost:8000"
    payload = {
        "prompt": "Create a simple cube and name it 'TestCube'",
        "api_key": "YOUR_OPENAI_KEY_HERE", # Replace with a real key for live testing
        "session_id": "test_session_123"
    }

    print(f"--- [INFO] Testing Swarm Manager at {url} ---")
    try:
        response = requests.post(f"{url}/run", json=payload, timeout=30)
        if response.status_code == 200:
            print("\n[SUCCESS] SWARM CONVERGED")
            data = response.json()
            print("Generated Code Sample:")
            print(data.get("code", "No code returned"))
            
            print("\n--- [CHECK] Checking Memory Persistence ---")
            if os.path.exists("backend/memory/test_session_123.md"):
                print("[OK] Memory file successfully created.")
            else:
                print("[WARNING] Memory file not found. Check backend permissions.")
        else:
            print(f"[ERROR] Error {response.status_code}: {response.text}")
    except Exception as e:
        print(f"[ERROR] FAILED: {str(e)}")

if __name__ == "__main__":
    test_swarm_e2e()
