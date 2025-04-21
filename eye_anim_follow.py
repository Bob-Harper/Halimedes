from vilib import Vilib
from time import sleep
from eyes.eye_loader import load_eye_profile
from eyes.eye_animator import EyeAnimator
import time

profile = load_eye_profile("real_owl")
animator = EyeAnimator(profile)
last_seen_face = time.time()
face_timeout = 0.75  # seconds before we reset to center
last_face_coords = (10, 10)  # start centered

def smooth_gaze_transition(from_x, from_y, to_x, to_y, from_pupil, to_pupil, steps=8, delay=0.015):
    for i in range(1, steps + 1):
        interp_x = round(from_x + (to_x - from_x) * (i / steps))
        interp_y = round(from_y + (to_y - from_y) * (i / steps))
        interp_pupil = from_pupil + (to_pupil - from_pupil) * (i / steps)
        animator.draw_gaze(interp_x, interp_y, pupil_size=interp_pupil)
        time.sleep(delay)

def smooth_gaze(to_x, to_y, to_pupil, steps=8, delay=0.015):
    animator.smooth_gaze_transition(
        animator.current_x, animator.current_y,
        to_x, to_y,
        animator.current_pupil, to_pupil,
        steps, delay
    )

def map_face_to_gaze(face_x, face_y):
    # Safe bounds (based on what we observed)
    face_x = max(100, min(540, face_x))  # Horizontal clamp
    face_y = max(100, min(380, face_y))  # Vertical clamp

    # Normalize to 0.0–1.0
    norm_x = (face_x - 100) / (540 - 100)
    norm_y = (face_y - 100) / (380 - 100)

    # flipping needed — image is correct
    x_off = norm_x * 20         # Left/Right is good
    y_off = (1.0 - norm_y) * 20 # Flip vertical: top becomes bottom
    return x_off, y_off



def main():
    global last_seen_face, last_face_coords
    Vilib.camera_start(vflip=False, hflip=False)
    Vilib.display(local=True, web=False)
    Vilib.face_detect_switch(True)

    print("[Hal Vision] Active — tracking enabled. Ctrl+C to stop.")

    try:
        while True:
            if Vilib.face_obj_parameter['n'] > 0:
                face_x = Vilib.detect_obj_parameter['human_x']
                face_y = Vilib.detect_obj_parameter['human_y']

                x_off, y_off = map_face_to_gaze(face_x, face_y)

                last_seen_face = time.time()
                last_face_coords = (x_off, y_off)

                smooth_gaze(x_off, y_off, to_pupil=1.2)

            else:
                time_since_seen = time.time() - last_seen_face

                if time_since_seen < face_timeout:
                    # Use last known position
                    x_off, y_off = last_face_coords
                    smooth_gaze(x_off, y_off, to_pupil=1.3)
                else:
                    # Timeout expired — return to center
                    smooth_gaze(10, 10, to_pupil=1.0)

            sleep(0.2)

    except KeyboardInterrupt:
        print("\n[Hal Vision] Deactivating...")

    finally:
        Vilib.camera_close()

if __name__ == "__main__":
    main()