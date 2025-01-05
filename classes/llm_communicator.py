import requests
import json


class LLMCommunicator:
    def __init__(self, host='192.168.0.101', port=5000):
        self.host = host
        self.port = port
        self.server_url = f"http://{self.host}:{self.port}/v1/chat/completions"  # Construct the full URL

    def send_to_server(self, text):
        headers = {"Content-Type": "application/json", "accept": "application/json"}
        # Use the custom formatted prompt
        data = json.dumps({
            "prompt": text  # Send the entire prompt with special tokens
        })

        try:
            print(f"Sending HTTP request to server {self.server_url}")
            response = requests.post(self.server_url, headers=headers, data=data)
            response.raise_for_status()  # Raise an error for bad HTTP responses
            return response.text
        except requests.exceptions.RequestException as e:
            print(f"Error while communicating with server: {e}")
            return "Error: Failed to get response from server"

    def get_response(self, text):
        response_text = self.send_to_server(text)
        return response_text
