import requests
import json

# URL of the prediction API
API_URL = "http://localhost:8000/predict"

# Sample payload for prediction
payload = {
    "runtimeMinutes": 180,
    "budget": 100000,
    "genres": ["Comedy", "Drama"],
    "production_companies": ["co0092633", "co0274103"],
    "languages": ["en", "nl"],
    "countries": ["US", "BE"],
    "rating": "R",
    "loc": "US"
}

# Send POST request to the API
response = requests.post(API_URL, json=payload)

# Check for successful response
if response.status_code == 200:
    data = response.json()
    print(f"Predicted success probability: {data['success_probability']:.4f}")
else:
    print(f"Error {response.status_code}: {response.text}")
