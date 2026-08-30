import requests  # type: ignore # noqa: F401
import json

def test_api():
    """
    Simulates a multi-turn request to verify persistent memory.
    """
    url = "http://localhost:8000/run"
    session_id = "test_persistence_user"
    
    # Payload for the first turn
    payload = {
        "prompt": "Create a red cube named 'MyCube'",
        "api_key": "your-api-key-here",
        "session_id": session_id,
        "model": "gpt-4o"
    }
    
    print(f"--- Sending Turn 1 to {url} ---")
    try:
        response = requests.post(url, json=payload, timeout=30)
        if response.status_code == 200:
            print("Turn 1 Success. Code generated.")
            print(f"Response: {response.json().get('code')[:100]}...")
            
            # Simulate a follow-up turn
            print(f"\n--- Sending Turn 2 (Follow-up) to {url} ---")
            payload["prompt"] = "Now move MyCube up by 5 units"
            response = requests.post(url, json=payload, timeout=30)
            
            if response.status_code == 200:
                print("Turn 2 Success. AI remembered 'MyCube'.")
                print(f"Response: {response.json().get('code')}")
            else:
                print(f"Turn 2 Error: {response.text}")
        else:
            print(f"Turn 1 Error: {response.text}")
            
    except Exception as e:
        print(f"Server is likely not running or timeout: {str(e)}")

if __name__ == "__main__":
    test_api()
