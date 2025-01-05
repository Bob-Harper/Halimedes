import socket
import json
import sounddevice as sd
from vosk import Model, KaldiRecognizer
from robot_hat import TTS

# Initialize TTS
tts = TTS(engine='espeak')
tts.espeak_params(amp=50, speed=130, gap=2, pitch=40)

def send_to_server(text, source, host='192.168.0.101', port=5000):
    data = json.dumps({"source": source, "text": text})
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((host, port))
        s.sendall(data.encode('utf-8'))
        response = s.recv(1024)
    # Decode the JSON response
    response_data = json.loads(response.decode('utf-8'))
    return response_data["response"]

def recognize_speech_vosk():
    model = Model("path/to/vosk_model/vosk-model-small-en-us-0.15")  # Update the path to the VOSK model
    recognizer = KaldiRecognizer(model, 16000)

    with sd.RawInputStream(samplerate=16000, blocksize=8000, dtype='int16',
                           channels=1) as stream:
        print("Listening... Press Ctrl+C to stop.")
        while True:
            data = stream.read(4000)
            if recognizer.AcceptWaveform(data):
                result = recognizer.Result()
                text = json.loads(result)["text"]
                if text:
                    return text

def main():
    print("AI LLM Generation Test begin")
    tts.lang("fr-FR")

    # Convert speech to text
    spoken_text = recognize_speech_vosk()
    if spoken_text:
        print(f"Recognized text: {spoken_text}")

        # Send the text to the server and get the response
        response_text = send_to_server(spoken_text, "Hal")  # Specify "Hal" or "Stygia" as the source
        print(f"Response from server: {response_text}")

        # Use TTS to speak the response
        tts.say(response_text)
    else:
        print("Could not understand the audio")

if __name__ == "__main__":
    main()

