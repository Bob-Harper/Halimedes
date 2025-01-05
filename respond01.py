import requests
from classes.tts import TTS
import sounddevice as sd
from vosk import Model, KaldiRecognizer
import sys
import re
import ollama
import json


# Initialize TTS
voice_path = '/home/msutt/hal/flitevox/cmu_us_jmk.flitevox'  # Update voice path
tts = TTS(voice_path=voice_path, duration_stretch=1.4, pitch=96)  # Adjust for Halimedes

def recognize_speech_vosk():
    """Recognize speech using Vosk and return the transcribed text."""
    model = Model("/home/msutt/hal/vosk_models/vosk-model-small-en-us-0.15")  # Update the path to Vosk model
    recognizer = KaldiRecognizer(model, 44100)  # Corrected sample rate
    device_index = 1  # Your mic device index

    with sd.RawInputStream(samplerate=44100, blocksize=8000, dtype='int16',
                           channels=1, device=device_index) as stream:
        print("Listening... Press Ctrl+Z to stop.")
        while True:
            data, overflowed = stream.read(8000)  # Read raw audio data

            audio_bytes = bytes(data)  # Convert to a bytes object

            if recognizer.AcceptWaveform(audio_bytes):  # If it accepts the audio
                result = recognizer.Result()
                print(f"Vosk result: {result}")
                try:
                    text = json.loads(result)["text"]
                    if text:
                        return text
                except json.JSONDecodeError:
                    print("Failed to decode JSON from Vosk result.")
                    return None

def send_to_server(system_prompt, spoken_text):
    server_url = "http://192.168.0.101:11434/api/chat/"
    headers = {"Content-Type": "application/json", "accept": "application/json"}

    # Build the prompt using the special tokens
    chat_response = json.dumps({
      "model": "llama3.2",
      "messages": [
        {
          "role": "system",
          "content": f"{system_prompt}"
        },
        {
          "role": "user",
          "content": f"{spoken_text}"
        },
      ],
      "stream": False
    })
    try:
        print(f"Sending HTTP request to server {server_url}")
        response = requests.post(server_url, headers=headers, data=chat_response)
        print(f"Initial Response: {response}")
        print(f"Response Text: {response.text}")
        response.raise_for_status()  # Raise an error for bad HTTP responses
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"Error while communicating with server: {e}")
        return "Error: Failed to get response from server"


def main():
    print("AI LLM Generation Test begins")
    tts.say("AI LLM Generation Test begins.")

    system_prompt = (
        "You are an alien robot that can respond in natural, conversational English. "
        "You are excited to be exploring this planet and learning all about it."
        "You prefer short sentences, and you are speaking with an 11 year old girl who likes science, uncommon animals, and anime."
    )

    # Recognize speech with Vosk
    spoken_text = recognize_speech_vosk()
    if spoken_text:
        print(f"Recognized text: {spoken_text}")
    try:
        chat_response = send_to_server(system_prompt, spoken_text)
        # Extract the message content
        chat_response_data = json.loads(chat_response)  # Parse the response JSON
        print(f"Generated Response: {chat_response_data}")
        if "message" in chat_response_data:
            message = chat_response_data["message"]
            content = message.get("content", "No response content found.")
        else:
            content = "Ow my head..  who slipped what into my drink....."

    except Exception as e:
        content = f"Something went wrong. I DO NOT LIKE BEING WRONG: {e}"

    print(f"Generated message: {content}")
    tts.say(content)


if __name__ == "__main__":
    main()

