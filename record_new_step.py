from picrawler import Picrawler
from time import sleep
import sys
import tty
import termios
import copy

crawler = Picrawler()
speed = 80

def readchar():
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(sys.stdin.fileno())
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch

manual = '''
Press keys on keyboard to control!
    w: Y++
    a: X--
    s: Y--
    d: X++
    r: Z++
    f: Z--
    1: Select right front leg
    2: Select left front leg
    3: Select left rear leg
    4: Select right rear leg
    Space: Print all leg coordinates & Save this step
    p: Play all saved step
    +: Increase movement increment
    -: Decrease movement increment
    esc: Quit
'''

new_step = []

def save_new_step():
    new_step.append(copy.deepcopy(crawler.current_step_all_leg_value()))

def play_all_new_step():
    for step in new_step:
        crawler.do_step(step, speed)
        sleep(0.6)

def print_modifier_status(increment):
    sys.stdout.write("\r\033[K")  # Clear line and return cursor to start
    print(f"Movement increment: {increment}", end='')

def main():
    print(manual)
    crawler.do_step('sit', speed)
    leg = 0
    coordinate = crawler.current_step_leg_value(leg)

    # Initial increment value
    increment = 5

    print_modifier_status(increment)

    while True:
        key = readchar()

        # Handle key presses
        if key == '\x1b':  # ESC key
            break
        elif key == '=':  # Increase movement increment
            increment += 1
            print_modifier_status(increment)
        elif key == '-':  # Decrease movement increment
            increment = max(1, increment - 1)  # Ensure increment does not go below 1
            print_modifier_status(increment)
        else:
            # Adjust coordinate based on movement increment
            if 'w' == key:
                coordinate[1] += increment
            elif 's' == key:
                coordinate[1] -= increment
            elif 'a' == key:
                coordinate[0] -= increment
            elif 'd' == key:
                coordinate[0] += increment
            elif 'r' == key:
                coordinate[2] += increment
            elif 'f' == key:
                coordinate[2] -= increment
            elif '1' == key:
                leg = 0
                coordinate = crawler.current_step_leg_value(leg)
            elif '2' == key:
                leg = 1
                coordinate = crawler.current_step_leg_value(leg)
            elif '3' == key:
                leg = 2
                coordinate = crawler.current_step_leg_value(leg)
            elif '4' == key:
                leg = 3
                coordinate = crawler.current_step_leg_value(leg)
            elif key == ' ':  # Space bar
                print("\n[[right front],[left front],[left rear],[right rear]]")
                print("saved new step")
                print(crawler.current_step_all_leg_value())
                save_new_step()
            elif key == 'p':
                play_all_new_step()

        sleep(0.05)
        crawler.do_single_leg(leg, coordinate, speed)

    print("\nQuit")

if __name__ == "__main__":
    main()
