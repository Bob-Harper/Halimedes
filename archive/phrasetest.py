import sys
import termios
import os
import tty
import subprocess  # For running the `flite` command

def getch():
    """Function to capture single key presses."""
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch

def speak_with_flite(voice_path, text):
    """Speak text using Flite directly."""
    try:
        cmd = ["flite", "-voice", voice_path, "-t", text]
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error running Flite: {e}")

def main():
    # Path to the Flite voice file
    voice_path = "/home/msutt/hal/flitevox/cmu_us_rms.flitevox"

    # Define a dictionary of phrases
    phrases = {
        "1": "What's up, boss?",
        "2": "Hey, you cannot do that.",
        "3": "Of course I can do that, watch me.",
        "4": "I cannot do that? But I just did.",
        "5": "Move it.",
        "6": "Goodnight human, I think it is cute that you always go to sleep expecting to wake up in the morning.",
    }

    print("Input key to play the phrase or 'q' to quit:")
    for key, phrase in phrases.items():
        print(f"{key}: {phrase}")
    print()

    while True:
        key = getch().lower()
        if key == 'q':
            print("Exiting.")
            break
        elif key in phrases:
            print(f"Speaking: {phrases[key]}")
            speak_with_flite(voice_path, phrases[key])  # Directly invoke Flite to speak
        else:
            print("Invalid input. Enter a number between 1 and 6 or 'q' to quit.")

if __name__ == "__main__":
    main()
