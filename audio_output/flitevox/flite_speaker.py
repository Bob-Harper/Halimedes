import subprocess
from helpers.global_config import VOICE_MODEL_PATH, VOICE_MODEL_NAME

def speak_with_flite(words):
    voice_path=VOICE_MODEL_PATH/VOICE_MODEL_NAME 
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

if __name__ == "__main__":
    speak_with_flite("I want to sing...  sing...  SING!!!")
