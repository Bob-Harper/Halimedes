import time
from pathlib import Path
from eyes.eye_loader import load_eye_profile
from eyes.eye_animator import EyeAnimator

gaze_sequence = [
    (0, 10),  # Left
    (20, 10), # Right
    (10, 0),  # Up
    (10, 20), # Down
    (10, 10)  # Center
]

def review_eye_profile(profile_name):
    profile = load_eye_profile(profile_name)
    animator = EyeAnimator(profile)

    print(f"\n[REVIEWING] {profile_name}")
    animator.draw_gaze(10, 10, pupil_size=1.0)
    time.sleep(0.8)
    animator.draw_gaze(10, 10, pupil_size=1.5)
    time.sleep(0.8)
    animator.draw_gaze(10, 10, pupil_size=0.5)
    time.sleep(0.8)
    animator.draw_gaze(10, 10, pupil_size=1.0)
    time.sleep(0.8)

    for x, y in gaze_sequence:
        animator.draw_gaze(x, y, pupil_size=1.0)
        time.sleep(1.0)

    time.sleep(0.5)

if __name__ == "__main__":
    profiles = sorted(Path("eyes/images").glob("*.json"))

    for profile_path in profiles:
        try:
            review_eye_profile(profile_path.stem)
        except Exception as e:
            print(f"[ERROR] {profile_path.stem}: {e}")
