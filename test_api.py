import requests

BASE_URL = "http://127.0.0.1:5000"

chatbot_data = {"selected_crop": "wheat", "city": "New York"}
response = requests.post(f"{BASE_URL}/get_chatbot_response", json=chatbot_data)

print("Chatbot API Response Code:", response.status_code)
print("Chatbot API Response:", response.json())  # Show full response
