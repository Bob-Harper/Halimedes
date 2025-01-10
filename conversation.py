import json
import sounddevice as sd
from vosk import Model, KaldiRecognizer
import subprocess
from ollama import Client

MAX_TOKEN_COUNT = 2048  # Example token limit for the model

# Global conversation history
conversation_history = [
    {
        'role': 'system',
        'content': 'You are Halimeedees, a quirky alien robot exploring Earth. Speak in a curious and funny tone. Keep your responses short, your audience is young and has a short attention span. Do not use asterisks or actions.',
    }
]


def truncate_history(conversation_history, max_tokens):
    """Truncate the conversation history while preserving the system prompt."""
    token_count = len(conversation_history[0]['content'].split())  # Start with system prompt tokens
    truncated_history = [conversation_history[0]]  # Always keep the system prompt

    # Iterate over messages from the end to preserve recent context
    for message in reversed(conversation_history[1:]):  # Skip the system prompt
        message_token_count = len(message['content'].split())
        if token_count + message_token_count > max_tokens:
            break
        truncated_history.insert(1, message)  # Insert after the system prompt
        token_count += message_token_count

    return truncated_history


def get_microphone_index(mic_name):
    """Find the device index for a given microphone name, with error handling."""
    devices = sd.query_devices()
    for idx, device in enumerate(devices):
        if mic_name in device["name"]:
            return idx
    print(f"Microphone '{mic_name}' not found! Available devices:")
    for idx, device in enumerate(devices):
        print(f"{idx}: {device['name']}")
    raise ValueError(f"Microphone '{mic_name}' not found!")


def send_to_server(text):
    """Send user input to the LLM server and get a response."""
    global conversation_history  # Use global to maintain context across calls

    # Add user message to the conversation history
    conversation_history.append({
        'role': 'user',
        'content': text,
    })

    # Truncate history to fit within the token limit
    conversation_history = truncate_history(conversation_history, MAX_TOKEN_COUNT)
    print(f"conversation_history:\n {conversation_history}\n")
    try:
        # Send the chat messages to the server
        client = Client(host='http://192.168.0.101:11434')
        response = client.chat(model='llama3.2', messages=conversation_history)
        response_text = response['message']['content']

        # Add assistant response to the conversation history
        conversation_history.append({
            'role': 'assistant',
            'content': response_text,
        })

        return response_text

    except Exception as e:
        print(f"Error during chat or speech: {e}")
        return "I'm sorry, I couldn't process that."


def recognize_speech_vosk():
    """Recognize speech using Vosk and return the transcribed text."""
    mic_name = "USB PnP Sound Device"  # Defined mic name
    device_index = get_microphone_index(mic_name)  # Find the mic index dynamically
    print(f"Using microphone: {mic_name} (Index: {device_index})")

    model_path = "/home/msutt/hal/vosk_models/vosk-model-small-en-us-0.15"  # Preserved model path
    model = Model(model_path)
    recognizer = KaldiRecognizer(model, 44100)  # Preserved sample rate

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


def speak_with_flite(words):
    """Speak the generated response using Flite."""
    voice_path = "/home/msutt/hal/flitevox/cmu_us_rms.flitevox"  # Preserved voice file path
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
    """Main loop to recognize speech, send to server, and speak response."""
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
