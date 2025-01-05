from time import sleep
from robot_hat import TTS
import socket

tts = TTS()


def send_to_server(text, host='192.168.0.101', port=5000):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((host, port))
        s.sendall(text.encode('utf-8'))
        response = s.recv(1024)
    return response.decode('utf-8')

def main():
    print("AI LLM Generation Test begin")
    tts.lang("en-US")

    # Convert speech to text (Placeholder)
    spoken_text = "Hello, I have detected your face and i recognize you."  # This should be the result of speech-to-text processing

    # Send the text to the server and get the response
    response_text = send_to_server(spoken_text)
    print(f"Response from server: {response_text}")

    # Use TTS to speak the response
    tts.say(response_text)

if __name__ == "__main__":
    main()
