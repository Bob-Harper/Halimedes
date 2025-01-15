import json
import sounddevice as sd
from vosk import Model, KaldiRecognizer
import subprocess
from ollama import Client


def get_microphone_index(mic_name):  # Find the device index for a given microphone name.
    for idx, device in enumerate(sd.query_devices()):
        if mic_name in device["name"]:
            return idx
    raise ValueError(f"Microphone '{mic_name}' not found!")


def send_to_server(text):
    print("AI LLM Chat Test Begin")
    client = Client(host='http://192.168.0.101:11434')
    # Conversation starter prompt
    messages = [
        {
            'role': 'system',
            'content': 'You are Halimeedees, a quirky alien robot exploring Earth. Speak in a curious and funny tone. Keep your responses short, your audience is yung and has a short attention span.  DO not use asterisks or actions.',
        },
        {
            'role': 'user',
            'content': text,
        },
    ]

    try:
        # Send the chat messages to the server
        response = client.chat(model='llama3.2', messages=messages)
        response_text = response['message']['content']
        return response_text

    except Exception as e:
        print(f"Error during chat or speech: {e}")


def recognize_speech_vosk():
    """Recognize speech using Vosk and return the transcribed text."""
    mic_name = "USB PnP Sound Device"
    # Get the device index dynamically
    device_index = get_microphone_index(mic_name)
    print(f"Using microphone: {mic_name} (Index: {device_index})")
    model = Model("/home/msutt/hal/vosk_models/vosk-model-small-en-us-0.15")  # small model.  keep the input simple when possible
    recognizer = KaldiRecognizer(model, 44100)  # default sample rate

    with sd.RawInputStream(samplerate=44100, blocksize=8000, dtype='int16',
                           channels=1, device=device_index) as stream:
        print("Listening... Press Ctrl+Z to stop.")
        while True:
            data, overflowed = stream.read(8000)  # Read raw audio data

            # Convert the raw buffer data to a bytes object
            audio_bytes = bytes(data)  # Convert to a bytes object

            # Pass the audio bytes directly to AcceptWaveform
            if recognizer.AcceptWaveform(audio_bytes):
                result = recognizer.Result()
                text = json.loads(result)["text"]
                if text:
                    return text
            # else:
                # Optionally print the partial result for debugging
                # partial_result = recognizer.PartialResult()
                # print(f"Partial result: {json.loads(partial_result)['partial']}")


def speak_with_flite(words):
    voice_path="/home/msutt/hal/flitevox/cmu_us_rms.flitevox"
    try:
        # Construct the Flite command
        command = [
            "flite",
            "-voice", voice_path,
            "-t", words
        ]
        # Execute the Flite command directly
        subprocess.run(command, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")
    except FileNotFoundError:
        print("Flite command not found. Ensure it is installed and in the PATH.")

def main():
    print("AI LLM Generation Test begins")
    try:
        while True:  # Infinite loop to continuously listen and respond
            # Recognize speech with Vosk
            spoken_text = recognize_speech_vosk()
            if spoken_text:
                print(f"Recognized text: {spoken_text}")

                # Send the recognized text to the LLM server
                response_text = send_to_server(spoken_text)
                print(f"Response from LLM server: {response_text}")

                # Use Flite to speak the response
                speak_with_flite(response_text)
            else:
                print("Could not understand the audio")
    except KeyboardInterrupt:
        print("\nExiting program.")

if __name__ == "__main__":
    main()

"""
IDEAS 
Use tools like PyAudio or sox for live noise filtering:
sox -d -n noiseprof noise.prof
sox input.wav output.wav noisered noise.prof 0.21

Add noise suppression in your Python code with libraries like noisereduce:
import noisereduce as nr
reduced_noise = nr.reduce_noise(y=audio_data, sr=sample_rate)

"""