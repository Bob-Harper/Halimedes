import time
import sys
import termios
import tty
from eyes.eye_loader import load_eye_profile
from eyes.eye_animator import EyeAnimator

def get_key():
    """Non-blocking keypress reader for Linux terminals"""
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        ch = sys.stdin.read(1)
        if ch == '\x1b':  # Arrow keys
            ch2 = sys.stdin.read(1)
            ch3 = sys.stdin.read(1)
            return ch + ch2 + ch3
        return ch
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

def run_manual_eye_control(profile_name):
    profile = load_eye_profile(profile_name)
    animator = EyeAnimator(profile)

    x = 10
    y = 10
    pupil = 1.0

    print("\n[MANUAL CONTROL MODE]")
    print("Arrows to move gaze, [ ] to change pupil, z = snap, space = smooth, r = reset, q = quit")

    while True:
        key = get_key()

        if key == 'q':
            print("\n[Exit]")
            break
        elif key == '\x1b[D':  # Left
            x = max(0, x - 1)
        elif key == '\x1b[C':  # Right
            x = min(20, x + 1)
        elif key == '\x1b[A':  # Up
            y = max(0, y - 1)
        elif key == '\x1b[B':  # Down
            y = min(20, y + 1)
        elif key == '[':
            pupil = max(profile.pupil_min, round(pupil - 0.02, 3))
        elif key == ']':
            pupil = min(profile.pupil_max, round(pupil + 0.02, 3))
        elif key == ' ':
            animator.smooth_gaze(x, y, pupil)
        elif key == 'z':
            animator.draw_gaze(x, y, pupil)
        elif key == 'r':
            x, y, pupil = 10, 10, 1.0
            animator.draw_gaze(x, y, pupil)

        print(f"[Gaze] X:{x}  Y:{y}  Pupil:{pupil:.2f}", end='\r')

if __name__ == "__main__":
    profile_name = "vector03"  # Change to any eye texture profile
    run_manual_eye_control(profile_name)
