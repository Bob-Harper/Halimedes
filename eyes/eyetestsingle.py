import time
import random
from eyes.eye_loader import load_eye_profile
from eyes.eye_animator import EyeAnimator


def run_eye_preview(profile_name):
    profile = load_eye_profile(profile_name)
    animator = EyeAnimator(profile)
    pupil_min = profile.pupil_min
    pupil_max = profile.pupil_max
    x_off = profile.x_off
    y_off = profile.y_off
    close_speed = profile.close_speed
    open_speed = profile.open_speed
    hold = profile.hold

    print(f"\n[PREVIEW] Now previewing: {profile_name}")

    # Step 1: Eyes open at neutral
    animator.dual_blink_open(pupil_size=1.0)
    time.sleep(0.4)

    # Step 2: Max dilation
    animator.dual_blink_cycle(
        pupil_size=pupil_max,
        x_off=x_off, y_off=y_off,
        close_speed=close_speed, open_speed=open_speed, hold=hold
    )
    time.sleep(0.4)

    # Step 3: Max contraction
    animator.dual_blink_cycle(
        pupil_size=pupil_min,
        x_off=x_off, y_off=y_off,
        close_speed=close_speed, open_speed=open_speed, hold=hold
    )
    time.sleep(0.4)

    # Step 4: Return to neutral
    animator.dual_blink_cycle(
        pupil_size=1.0,
        x_off=x_off, y_off=y_off,
        close_speed=close_speed, open_speed=open_speed, hold=hold
    )
    time.sleep(0.5)

    # Step 5: Gaze animation loop
    gaze_coords = [(x, y) for x in (0, 10, 20) for y in (0, 10, 20)]
    end_time = "infinite"
    while end_time == "infinite":
        new_x, new_y = random.choice(gaze_coords)
        pupil = snap(random.uniform(pupil_min, pupil_max), step=.1)
        animator.smooth_gaze(new_x, new_y, pupil)
        time.sleep(random.uniform(0.4, 1.0))

        if random.random() < 0.15:
            animator.dual_blink_cycle(
                pupil_size=pupil,
                close_speed=close_speed,
                open_speed=open_speed,
                hold=hold
            )


def snap(value, step=0.01):
    return round(step * round(value / step), 2)


if __name__ == "__main__":
    # CHANGE THIS to whatever profile you want to test.  current suggested default: - googly01 * ACTUAL default
 
    profile_name = "vector03"  # <- filename without .json extension.

    try:
        run_eye_preview(profile_name)
    except Exception as e:
        print(f"[ERROR] Failed to preview '{profile_name}': {e}")

"""
Eye textures with working CFG values:

- vector04 * possible defaultvector04
- hitech28
- hitech06
- hitech10
- hitech13
- hitech16 * possible default
- googly01 * ACTUAL default
- bluetech01 * possible default

  "pupil_min": 0.975,
  "pupil_max": 1.3,
"""