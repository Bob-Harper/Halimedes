from vilib import Vilib
from time import sleep

def main():
    Vilib.camera_start(vflip=False, hflip=False)
    Vilib.display(local=False, web=False)
    print("Camera initialized. Press 'q' to quit.")

    while True:
        key = input().lower()
        if key == 'q':
            break
        sleep(0.5)

    Vilib.camera_close()
    print("Camera closed.")

if __name__ == "__main__":
    main()
