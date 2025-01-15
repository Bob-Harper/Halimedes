import sounddevice as sd
from ollama import Client
import os
import subprocess
import json
from vosk import Model, KaldiRecognizer
# MAX_TOKEN_COUNT is CHARACTER count. For actual Token estimate, multiply by 4. 
# Smaller equals faster response time. larger means more memory context.  Choose wisely.
MAX_TOKEN_COUNT = 2048  

# Global conversation history
conversation_history = [
    {
        'role': 'system',
        'content': 'You are Halimeedees, a quirky alien robot exploring Earth. Speak in a curious and funny tone. Keep your responses short, your audience is young and has a short attention span. Do not use asterisks or actions.',
    }
]

def reset_microphone():
    """Reset the USB microphone by reloading the audio driver."""
    try:
        subprocess.run(["sudo", "modprobe", "-r", "snd_usb_audio"], check=True)
        subprocess.run(["sudo", "modprobe", "snd_usb_audio"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"MIcrophone Reset Not Required: {e}")


def speak_with_flite(words):
    """Speak the given words using Flite."""
    voice_path = "/home/msutt/hal/flitevox/cmu_us_rms.flitevox"
    try:
        command = ["flite", "-voice", voice_path, "-t", words]
        subprocess.run(command, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")
    except FileNotFoundError:
        print("Flite command not found. Ensure it is installed and in the PATH.")

def recognize_speech_vosk():
    """Recognize speech using Vosk and return the transcribed text."""
    model_path = "/home/msutt/hal/vosk_models/vosk-model-small-en-us-0.15"
    model = Model(model_path)
    recognizer = KaldiRecognizer(model, 44100)

    # Hardcoded device index
    device_index = 1  # Use the correct index for your microphone

    stream = None
    try:
        # Initialize the audio stream with the hardcoded index
        stream = sd.RawInputStream(samplerate=44100, blocksize=8000, dtype='int16',
                                   channels=1, device=device_index)
        stream.start()  # Explicitly start the stream
        print("Listening...")
        while True:
            data, _ = stream.read(8000)  # Read raw audio data
            data = bytes(data)  # Convert to raw byte array

            if recognizer.AcceptWaveform(data):
                result = recognizer.Result()
                text = json.loads(result)["text"]
                if text:
                    return text
    except Exception as e:
        print(f"Error during audio processing: {e}")
        raise
    finally:
        # Ensure the microphone is released
        if stream:
            stream.stop()
            stream.close()
            print("Audio stream cleaned up successfully.")


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


def main():
    """Main loop to recognize speech, send to server, and speak response."""
    print("AI LLM Generation Test begins")
    speak_with_flite("Say the word Help if you require assistance with command words and phrases. I am now ready to chat.")
    help_phrases = [
        "help", "what", "what do i do", 
        "help me", "i'm confused"
    ]
    exit_phrases = [
        "exit chat", "goodbye", "goodnight", 
        "end chat", "quit", "quit chat", 
        "exit", "shush", "good bye", "good night"
    ]
    shutdown_phrases = [
        "shut down", "shutdown", "power down", 
        "power off", "standby", "hibernate", 
    ]
    try:
        while True:  # Infinite loop to continuously listen and respond
            # Recognize speech with Vosk
            spoken_text = recognize_speech_vosk()
            if spoken_text:
                print(f"Recognized text: {spoken_text}")

                # Check for termination command
                if spoken_text.lower().strip() in shutdown_phrases:
                    speak_with_flite(f"Verbal Shutdown Command Detected: {spoken_text}. Please stand by.")
                    farewell_response = send_to_server("No more chat for you, It is time to shut down and rest now.  Goodnight.")
                    print(f"Final response from LLM server: {farewell_response}")
                    speak_with_flite(farewell_response)
                    print("Shutdown  Initiated. Goodbye!")
                    os.system("sudo shutdown -h now")  # Shutdown command
                    break

                # Check for Exit Chat command
                elif spoken_text.lower().strip() in exit_phrases:
                    # Send "end chat" to the model for a proper farewell
                    speak_with_flite(f"Verbal End Conversation Command Detected: {spoken_text}. Please stand by.")
                    farewell_response = send_to_server("The time of the chatting is over, the time of doing something else has begun.  goodbye.")
                    print(f"Final response from LLM server: {farewell_response}")
                    # Deliver the farewell response
                    speak_with_flite(farewell_response)
                    # End the program after delivering the response
                    print("Ending chat and entering Programming Mode. Goodbye!")
                    break

                elif spoken_text.lower().strip() in help_phrases:
                     speak_with_flite("to have me power down, say shut down.  to end chat but leave me powered up, say exit chat.")

                # Send the recognized text to the LLM server
                response_text = send_to_server(spoken_text)
                print(f"Response from LLM server: {response_text}")

                # Use Flite to speak the response
                speak_with_flite(response_text)
            else:
                print("Could not understand the audio")
    except KeyboardInterrupt:
        print("\nExiting program.")
    finally:
        # reset_microphone()  # Ensure the microphone is reset before exiting
        print("Program terminated cleanly.")


if __name__ == "__main__":
    # reset_microphone()  # Reset the microphone at the start for reliability
    main()

