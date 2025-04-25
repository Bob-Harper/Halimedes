# test_eye_animator.py
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent / "eyes"))
import time
from eyes.eye_loader import load_eye_profile
from eyes.eye_animator import EyeAnimator
from eyes.core.blink_engine import BlinkEngine


def main():
    print("Halimedes Sanity Check: INITIATING")
    try:
        profile = load_eye_profile("googly01", config_dir="eyes/eye_assets")
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

    gaze_modes = ["center", "left", "right", "up", "down", "wander"]

    for mood in expressions:
        try:
            print(f"Setting expression: {mood}")
            hal.transition_expression(mood)  # or sad, skeptical, whatever
        except Exception as e:
            print(f"Expression '{mood}' failed: {e}")
            break

    for mode in gaze_modes:
        try:
            print(f"Gaze mode: {mode}")
            hal.apply_gaze_mode(mode)
            time.sleep(0.4)
        except Exception as e:
            print(f"Gaze mode '{mode}' failed: {e}")
            break

    print("Finished sanity pass. If nothing exploded, Hal is operational.")
    hal.apply_gaze_mode(mode)
if __name__ == "__main__":
    main()
