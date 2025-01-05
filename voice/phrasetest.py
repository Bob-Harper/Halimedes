import sys
import termios
import tty
from robot_hat import TTS
from voice.staticphrase import HalimedesPhrases  # Assuming your module where you define phrases

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
    tts = TTS(engine='espeak')
    tts.espeak_params(amp=180, speed=160, gap=1, pitch=5)

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

    def move_it(self):
        word = "Move bitch, get out the way."
        self.tts.say(word)

if __name__ == "__main__":
    main()
