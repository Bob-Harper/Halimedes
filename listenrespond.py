import socket
import json
import sounddevice as sd
from vosk import Model, KaldiRecognizer
from robot_hat import TTS
import sys
import ctypes

# Manually add the virtual environment site-packages to sys.path
venv_path = "/home/msutt/hal/venv/lib/python3.11/site-packages"  # Update the Python version if different
sys.path.insert(0, venv_path)

# Initialize TTS
voice_path = '/home/msutt/hal/flitevox/cmu_us_jmk.flitevox'  # Update voice path
tts = TTS(voice_path=voice_path, duration_stretch=1.2, pitch=70)  # Adjust for Halimedes

def send_to_server(text, source, host='192.168.0.101', port=5000):
    """Send the recognized text to the LLM server and return the response."""
    data = json.dumps({"source": source, "text": text})
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((host, port))
        s.sendall(data.encode('utf-8'))
        response = s.recv(1024)
    response_data = json.loads(response.decode('utf-8'))
    return response_data["response"]

def recognize_speech_vosk():
    """Recognize speech using Vosk and return the transcribed text."""
    model = Model("/home/msutt/hal/vosk_models/vosk-model-small-en-us-0.15")  # Update the path to Vosk model
    recognizer = KaldiRecognizer(model, 44100)  # Corrected sample rate
    # Specify the microphone device index. This should be 1 as per your `arecord` results.
    device_index = 1

    with sd.RawInputStream(samplerate=44100, blocksize=8000, dtype='int16',
                           channels=1, device=device_index) as stream:
        print("Listening... Press Ctrl+Z to stop.")
        while True:
            data, overflowed = stream.read(8000)  # Read raw audio data, same blocksize as before

            # Convert the raw buffer data to a bytes object
            audio_bytes = bytes(data)  # Convert to a bytes object

            # Pass the audio bytes directly to AcceptWaveform
            if recognizer.AcceptWaveform(audio_bytes):  # No need for ctypes conversion
                result = recognizer.Result()
                text = json.loads(result)["text"]
                if text:
                    return text
            else:
                # Optionally print the partial result for debugging
                partial_result = recognizer.PartialResult()
                print(f"Partial result: {json.loads(partial_result)['partial']}")

def list_audio_devices():
    devices = sd.query_devices()
    for i, device in enumerate(devices):
        print(f"Device {i}: {device['name']} (Input Channels: {device['max_input_channels']}, Output Channels: {device['max_output_channels']})")


def main():
    print("AI LLM Generation Test begins")
    # list_audio_devices()
    # Recognize speech with Vosk
    spoken_text = recognize_speech_vosk()
    if spoken_text:
        print(f"Recognized text: {spoken_text}")

        # Send the recognized text to the LLM server
        response_text = send_to_server(spoken_text, "Halimedes")  # Specify the source as "Halimedes"
        print(f"Response from LLM server: {response_text}")

        # Use TTS to speak the response
        tts.say(response_text)
    else:
        print("Could not understand the audio")

if __name__ == "__main__":
    main()
