import subprocess

def speak_with_flite(words, voice_path="/home/msutt/hal/flitevox/cmu_us_rms.flitevox"):
    """
    Speak words using Flite via a direct subprocess call.
    :param words: Text to speak
    :param voice_path: Path to the Flite voice file
    """
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
    speak_with_flite("Testing sound output")
