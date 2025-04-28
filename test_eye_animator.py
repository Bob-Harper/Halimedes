import asyncio
from eyes.eye_loader import load_eye_profile
from eyes.eye_animator import EyeAnimator
from eyes.core.blink_engine import BlinkEngine

async def main():
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
    await asyncio.sleep(1)           # ← non-blocking
    print("Profile loaded, animator online.")
    # start blinking in the background
    blink_task = asyncio.create_task(hal.idle_blink_loop())

    for mood in ["test", "happy","sad","angry","focused","skeptical","surprised","asleep","neutral"]:
        print(f"Setting expression: {mood}")
        try:
            await hal.smooth_transition_expression(mood)
            await asyncio.sleep(2)
            for mode in ["center","left","center","right","center","up","center","down","center","wander"]:
                print(f"Gaze mode: {mode}")
                hal.apply_gaze_mode(mode)
                await asyncio.sleep(1)
        except Exception as e:
            print(f"Expression '{mood}' failed: {e}")
            break

    print("Finished sanity pass. Hal is operational.")
    blink_task.cancel()
if __name__ == "__main__":
    asyncio.run(main())
