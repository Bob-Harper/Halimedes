from ollama import Client
import subprocess

# Configure the client to point to the remote server
client = Client(host='http://192.168.0.101:11434')

def speak_with_flite(words, voice_path="/home/msutt/hal/flitevox/cmu_us_rms.flitevox"):
    """Speak words using Flite."""
    try:
        command = [
            "flite",
            "-voice", voice_path,
            "-t", words
        ]
        subprocess.run(command, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")
    except FileNotFoundError:
        print("Flite command not found. Ensure it is installed and in the PATH.")

def main():
    print("AI LLM Chat Test Begin")

    # Conversation starter prompt
    messages = [
        {
            'role': 'system',
            'content': 'You are Halimedes, a quirky alien robot exploring Earth. Speak in a curious and funny tone. Keep your responses short, your audience is yung and has a short attention span.  DO not use asterisks or actions.',
        },
        {
            'role': 'user',
            'content': 'Tell me about ball pythons!',
        },
    ]

    try:
        # Send the chat messages to the server
        response = client.chat(model='llama3.2', messages=messages)
        response_text = response['message']['content']

        print(f"\nResponse from server: {response_text}")

        # Speak the response using Flite
        speak_with_flite(response_text)

    except Exception as e:
        print(f"Error during chat or speech: {e}")

if __name__ == "__main__":
    main()
