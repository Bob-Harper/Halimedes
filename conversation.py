import sounddevice as sd
from ollama import Client
from voice_utils import reset_microphone, recognize_speech_vosk, speak_with_flite
import os

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
    try:
        while True:  # Infinite loop to continuously listen and respond
            # Recognize speech with Vosk
            spoken_text = recognize_speech_vosk()
            if spoken_text:
                print(f"Recognized text: {spoken_text}")

                # Check for termination command
                if spoken_text.lower().strip() == "shut down":
                    farewell_response = send_to_server("No more chat for you, It is time to shut down and rest now.  Goodnight.")
                    print(f"Final response from LLM server: {farewell_response}")
                    speak_with_flite(farewell_response)
                    print("Ending chat. Goodbye!")
                    os.system("sudo shutdown -h now")  # Shutdown command
                    break

                # Check for Exit Chat command
                elif spoken_text.lower().strip() == "exit chat":
                    # Send "end chat" to the model for a proper farewell
                    farewell_response = send_to_server("The time of the chatting is over, the time of doing something else has begun.  goodbye.")
                    print(f"Final response from LLM server: {farewell_response}")
                    # Deliver the farewell response
                    speak_with_flite(farewell_response)
                    # End the program after delivering the response
                    print("Ending chat. Goodbye!")
                    break

                #elif spoken_text.lower().strip() == "dance":
                #     perform_dance_move()  # Hypothetical function for movement
                #     speak_with_flite("Did you like my dance?")

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

