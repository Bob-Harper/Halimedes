import requests
import json

host = '192.168.0.101'  # Your server's IP
port = 5000             # The port you're using for the LLM server
endpoint = "/v1/chat/completions"  # The correct endpoint from the log
url = f"http://{host}:{port}{endpoint}"  # Construct the full URL

test_data = {
    "source": "Test",
    "text": "Hello, server!"
}

# Convert the test_data to JSON format
constructed_prompt_json = json.dumps(test_data)

# Headers for the HTTP request
headers = {
    "Content-Type": "application/json"
}

try:
    print(f"Sending HTTP request to server {url}")
    # Send the request using 'data' and 'headers', similar to Stygia's implementation
    response = requests.post(url, headers=headers, data=constructed_prompt_json)

    # Raise an error if the response code is not 2XX
    response.raise_for_status()

    # Print response from the server
    print(f"Response status code: {response.status_code}")
    print(f"Response from server: {response.text}")
except requests.exceptions.RequestException as e:
    print(f"Error: {e}")
