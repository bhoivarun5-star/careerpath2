import os
import requests
import json

OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY", "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")
OPENROUTER_MODEL = os.environ.get("OPENROUTER_MODEL", "google/gemma-3-27b-it:free")
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

def test_api():
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": OPENROUTER_MODEL,
        "messages": [
            {"role": "user", "content": "Analyze a simple resume for a Junior Web Developer and return a JSON object with: 'candidate_name', 'summary', 'score' (int), and 'roadmap' (a list of 2 phases). Return ONLY the JSON."},
        ],
        "max_tokens": 1000,
    }
    
    print(f"Testing API with model: {OPENROUTER_MODEL}")
    try:
        response = requests.post(OPENROUTER_URL, headers=headers, json=payload, timeout=30)
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            print("Response content:")
            print(json.dumps(response.json(), indent=2))
        else:
            print("Error response:")
            print(response.text)
            with open("api_error.json", "w") as f:
                f.write(response.text)
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    test_api()
