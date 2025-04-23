# test_eye_animator.py
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent / "eyes"))
import time
from eyes.eye_loader import load_eye_profile
from eyes.eye_animator import EyeAnimator

def main():
    print("🔥 Halimedes Sanity Check: INITIATING")
    try:
        profile = load_eye_profile("vector03", config_dir="eyes/eye_assets")
        hal = EyeAnimator(profile)
    except Exception as e:
        print(f"💥 INIT FAILURE: {e}")
        return

    print("✅ Profile loaded, animator online.")

    expressions = [
        "neutral", "happy", "sad", "angry",
        "focused", "skeptical", "surprised", "asleep"
    ]

    gaze_modes = ["center", "left", "right", "up", "down", "wander"]

    for mood in expressions:
        try:
            print(f"🧠 Setting expression: {mood}")
            hal.set_expression(mood)
            time.sleep(0.5)
            hal.blink()
        except Exception as e:
            print(f"💥 Expression '{mood}' failed: {e}")
            break

    for mode in gaze_modes:
        try:
            print(f"👀 Gaze mode: {mode}")
            hal.apply_gaze_mode(mode)
            time.sleep(0.4)
        except Exception as e:
            print(f"💥 Gaze mode '{mode}' failed: {e}")
            break

    print("✅ Finished sanity pass. If nothing exploded, Hal is operational.")

if __name__ == "__main__":
    main()
