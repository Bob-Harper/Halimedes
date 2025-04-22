from vilib import Vilib
from time import sleep
import termios
import tty
import sys

def get_key():
    """Reads a single character from input (non-blocking)."""
    fd = sys.stdin.fileno()
    old = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        return sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old)

def main():
    Vilib.camera_start(vflip=False, hflip=False)
    Vilib.display(local=True, web=False)
    Vilib.face_detect_switch(True)

    print("\n[Face Position Logger]")
    print("Move your face to a position, then press:")
    print("  Q = Top Left     E = Top Right")
    print("  Z = Bottom Left  C = Bottom Right")
    print("  S = Center       SPACE = Raw log")
    print("  X = Exit\n")

    try:
        while True:
            face_data = Vilib.detect_obj_parameter
            print("[DEBUG] face_data:", face_data)  # <- drop it here
            face_x = face_data.get('human_x', None)
            face_y = face_data.get('human_y', None)
            faces = face_data.get('human_n', 0)

            key = get_key().lower()

            if key == 'x':
                print("\n[Logger] Exit.")
                break

            if faces > 0 and face_x is not None and face_y is not None:
                label = {
                    'q': "Top Left",
                    'e': "Top Right",
                    'z': "Bottom Left",
                    'c': "Bottom Right",
                    's': "Center",
                    ' ': "Raw Snapshot"
                }.get(key, None)

                if label:
                    print(f"[{label}] x: {face_x}, y: {face_y}")
                else:
                    print(f"[?] Unmapped key: {key}")
            else:
                print("[!] No face detected.")

            sleep(0.1)

    except KeyboardInterrupt:
        print("\n[Logger] Interrupted by user.")

    finally:
        Vilib.camera_close()

if __name__ == "__main__":
    main()
