import time
import random
from pathlib import Path
from eyes.eye_loader import load_eye_profile
from eyes.eye_animator import EyeAnimator

def run_eye_preview(profile_name, duration=12):
    profile = load_eye_profile(profile_name)
    animator = EyeAnimator(profile)

    print(f"\n[PREVIEW] {profile_name}")

    # Step 1: Normal open
    animator.dual_blink_open(pupil_size=1.0)
    time.sleep(0.4)

    # Step 2: Blink to max dilation
    animator.dual_blink_cycle(
        pupil_size=1.5,
        x_off=10, y_off=10,
        close_speed=0.01, open_speed=0.02, hold=0.08
    )
    time.sleep(0.4)

    # Step 3: Blink to max contraction
    animator.dual_blink_cycle(
        pupil_size=0.5,
        x_off=10, y_off=10,
        close_speed=0.01, open_speed=0.025, hold=0.08
    )
    time.sleep(0.4)

    # Step 4: Blink back to neutral
    animator.dual_blink_cycle(
        pupil_size=1.0,
        x_off=10, y_off=10,
        close_speed=0.01, open_speed=0.02, hold=0.08
    )
    time.sleep(0.5)

    # Gaze animation loop — fixed duration
    gaze_coords = [(x, y) for x in (0, 10, 20) for y in (0, 10, 20)]
    current_x, current_y = 10, 10
    end_time = time.time() + duration

    while time.time() < end_time:
        new_x, new_y = random.choice(gaze_coords)
        pupil = random.uniform(0.8, 1.4)
        animator.smooth_gaze(new_x, new_y, pupil)
        current_x, current_y = new_x, new_y
        time.sleep(random.uniform(0.4, 1.0))

        if random.random() < 0.15:
            animator.dual_blink_cycle(
                pupil_size=pupil,
                x_off=current_x, y_off=current_y,
                close_speed=0.015, open_speed=0.03, hold=0.05
            )


if __name__ == "__main__":
    eye_profiles = list(Path("eyes/images").glob("*.json"))

    for profile_path in eye_profiles:
        try:
            run_eye_preview(profile_path.stem)
        except Exception as e:
            print(f"[ERROR] {profile_path.stem}: {e}")
