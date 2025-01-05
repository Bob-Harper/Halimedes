import sys
import termios
import tty
from classes.tts import TTS  # Your updated TTS class
from voice.staticphrase import HalimedesPhrases  # Assuming this handles the phrases for Halimedes

def getch():
    """Function to capture single key presses"""
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(sys.stdin.fileno())
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch

def main():
    # Specific settings for Halimedes' voice
    voice_path = '/home/msutt/hal/flitevox/cmu_us_jmk.flitevox'
    tts = TTS(voice_path=voice_path, duration_stretch=1.2, pitch=70)
    tts.set_volume(100)  # Set volume from 1% to 100%
    # Pass TTS instance to the HalimedesPhrases class
    phrases_module = HalimedesPhrases(tts)

    print("Input key to play the phrase or 'q' to quit:")
    print("1: Whats up, boss?")
    print("2: Hey, you cannot do that.")
    print("3: Of course I can do that, watch me.")
    print("4: I cannot do that? But I just did.")
    print("5: Move it.")
    print("6: Goodnight human, I think it is cute that you always go to sleep expecting to wake up in the morning.")
    print()

    while True:
        key = getch().lower()
        if key == 'q':
            break
        elif key in ['1', '2', '3', '4', '5', '6']:
            phrases_module.speak_phrase(int(key))
        else:
            print("Invalid input. Enter a number between 1 and 6 or 'q' to quit.")

if __name__ == "__main__":
    main()
