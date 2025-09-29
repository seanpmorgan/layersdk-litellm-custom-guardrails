# test_api_key.py
import os
import json
import litellm

# Load from secrets.json directly
with open('secrets.json') as f:
    secrets = json.load(f)

api_key = secrets.get("GEMINI_API_KEY")
print(f"API key from secrets: {api_key[:20]}...")

# Set and test
os.environ["GEMINI_API_KEY"] = api_key

try:
    response = litellm.completion(
        model="gemini/gemini-2.0-flash-exp",
        messages=[{"role": "user", "content": "test"}],
        max_tokens=10
    )
    print("API key works:", response.choices[0].message.content)
except Exception as e:
    print(f"API key failed: {e}")