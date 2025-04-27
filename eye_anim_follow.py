# hal_face_tracker.py
import time
import random
from vilib import Vilib
from eyes.eye_loader import load_eye_profile
from eyes.eye_animator import EyeAnimator

# === Initialization ===
profile = load_eye_profile("vector03")  # or "real_owl", up to you
animator = EyeAnimator(profile)

# Face tracking parameters
last_seen_face = time.time()
face_timeout = 0.75  # seconds before resetting to center
last_face_coords = (10, 10)  # Default center
last_blink_time = time.time()
blink_interval = random.uniform(8, 10)  # Randomize first blink


def map_face_to_gaze(face_x, face_y):
    """ Map 320x240 face center pixel to 0-20 gaze offsets """
    x_off = int(face_x / 16)  # 320 / 20 = 16
    y_off = int(face_y / 12)  # 240 / 20 = 12
    x_off = max(0, min(20, x_off))
    y_off = max(0, min(20, y_off))
    return x_off, y_off


def main():
    global last_seen_face, last_face_coords, last_blink_time, blink_interval

    print("[Hal Vision] Activating...")
    Vilib.camera_start(vflip=False, hflip=False)
    Vilib.display(local=True, web=False)  # Optional
    Vilib.face_detect_switch(True)

    try:
        while True:
            if Vilib.face_obj_parameter['n'] > 0:
                face_x = Vilib.detect_obj_parameter['human_x']
                face_y = Vilib.detect_obj_parameter['human_y']

                x_off, y_off = map_face_to_gaze(face_x, face_y)

                last_seen_face = time.time()
                last_face_coords = (x_off, y_off)

                animator.direct_gaze(x_off, y_off, pupil=1.3)

            else:
                time_since_seen = time.time() - last_seen_face

                if time_since_seen < face_timeout:
                    x_off, y_off = last_face_coords
                    animator.direct_gaze(x_off, y_off, pupil=1.3)
                else:
                    animator.direct_gaze(x_off, y_off, pupil=1.1)

            # BLINK CHECK
            now = time.time()
            if now - last_blink_time > blink_interval:
                animator.blink()
                last_blink_time = now
                blink_interval = random.uniform(4, 10)

            time.sleep(0.2)

    except KeyboardInterrupt:
        print("\n[Hal Vision] Deactivating...")

    finally:
        Vilib.camera_close()


if __name__ == "__main__":
    main()
