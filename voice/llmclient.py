from robot_hat import TTS
import socket
import json

tts = TTS(engine='espeak')
tts.espeak_params(amp=50, speed=130, gap=2, pitch=40)  # amp = volume, speed = 80 to 260, gap = time between words, pitch 0-98 deep or high voice


def send_to_server(text, source, host='192.168.0.101', port=5000):
    data = json.dumps({"source": source, "text": text})
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((host, port))
        s.sendall(data.encode('utf-8'))
        response = s.recv(1024)
    # Decode the JSON response
    response_data = json.loads(response.decode('utf-8'))
    return response_data["response"]

def main():
    print("AI LLM Generation Test begin")
    tts.lang("fr-FR")

    # Convert speech to text (Placeholder)
    # spoken_text = "So, hal, what are we going to do tonight?  what is our plan, man?"  # This should be the result of speech-to-text processing
    spoken_text = "Your human has sent you on a quest to find an object.  FInd a funny way to say  I FOUND IT: "  # This should be the result of speech-to-text processing

    # Send the text to the server and get the response
    response_text = send_to_server(spoken_text, "Hal")  # Specify "Hal" or "Stygia" as the source
    print(f"Response from server: {response_text}")

    # Use TTS to speak the response
    tts.say(response_text)

if __name__ == "__main__":
    main()
