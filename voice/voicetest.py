import curses
from robot_hat import TTS

tts = TTS(engine='espeak')
tts.espeak_params(amp=180, speed=160, gap=1, pitch=5)

# Clearer manual prompt without unnecessary details
manual = '''
Input key to call the function!
    Press 't' to speak text
    Press 'q' to quit
'''

def main(stdscr):
    stdscr.clear()
    stdscr.addstr(manual)
    stdscr.refresh()

    while True:
        key = stdscr.getch()  # Get single key press
        if key == ord('t'):
            word = "Goodnight human, I think it is cute that you always go to sleep expecting to wake up in the morning."
            tts.say(word)
        elif key == ord('q') or key == ord('Q'):
            break

if __name__ == "__main__":
    curses.wrapper(main)
