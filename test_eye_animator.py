# test_eye_animator.py
from helpers.global_config import EYE_ASSETS_PATH
import time
from eyes.eye_loader import load_eye_profile
from eyes.eye_animator import EyeAnimator
from eyes.core.blink_engine import BlinkEngine


def main():
    print("Halimedes Sanity Check: INITIATING")
    try:
        profile = load_eye_profile("real_owl")
        hal = EyeAnimator(profile)
        hal.blinker = BlinkEngine(hal.drawer)
    except Exception as e:
        print(f"INIT FAILURE: {e}")
        return
    print("DRAW TEST: Centered eye, no expression")
    hal.drawer.gaze_cache.clear()
    hal.draw_gaze(10, 10, 1.0)
    time.sleep(1)
    print("Profile loaded, animator online.")

    expressions = [
        "happy", "sad", "angry",
        "focused", "skeptical", "surprised", "asleep", "neutral", 
    ]

    # for mood in expressions:
    #     try:
    #         print(f"Setting expression: {mood}")
    #         hal.transition_expression(mood)  # or sad, skeptical, whatever
    #     except Exception as e:
    #         print(f"Expression '{mood}' failed: {e}")
    #         break

    gaze_modes = ["center", "left", "center", "right", "center", "up", "center", "down", "center", "wander"]

    for mode in gaze_modes:
        try:
            print(f"Gaze mode: {mode}")
            hal.apply_gaze_mode(mode)
            time.sleep(1.4)
        except Exception as e:
            print(f"Gaze mode '{mode}' failed: {e}")
            break

    print("Finished sanity pass. If nothing exploded, Hal is operational.")
    hal.apply_gaze_mode(mode)
if __name__ == "__main__":
    main()
