import socket
import json

class TTSFLITE:
    """Text to speech class using Flite"""
    FLITE = 'flite'

    def __init__(self, voice_path, duration_stretch=1.0, pitch=120):
        """
        Initialize TTSFLITE with Flite-specific parameters.

        :param voice_path: Path to the Flite voice file.
        :param duration_stretch: Stretch factor for cadence.
        :param pitch: Target pitch (fundamental frequency).
        """
        self.voice_path = voice_path
        self.duration_stretch = duration_stretch
        self.pitch = pitch

    def say(self, words):
        """Speak the words using Flite."""
        cmd = (f'flite -voice {self.voice_path} -setf duration_stretch={self.duration_stretch} '
               f'-setf int_f0_target_mean={self.pitch} -t "{words}"')
        os.system(cmd)

# Initialize Flite TTS
tts = TTSFLITE(voice_path="/home/msutt/hal/flitevox/cmu_us_rms.flitevox", duration_stretch=1.0, pitch=120)

def send_to_server(text, source, host='192.168.0.101', port=11434):
    """Send a query to the server and get a response."""
    data = json.dumps({"source": source, "text": text})
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((host, port))
        s.sendall(data.encode('utf-8'))
        response = s.recv(1024)
    # Decode the JSON response
    response_data = json.loads(response.decode('utf-8'))
    return response_data["response"]

def main():
    print("AI LLM Generation Test Begin")

    # Example input
    spoken_text = "Your human has sent you on a quest to find an object. Find a funny way to say 'I FOUND IT':"

    # Send the text to the server and get the response
    response_text = send_to_server(spoken_text, "Hal")  # Specify "Hal" or "Stygia" as the source
    print(f"Response from server: {response_text}")

    # Use Flite TTS to speak the response
    tts.say(response_text)

if __name__ == "__main__":
    main()
