import asyncio
from eyes.eye_loader import load_eye_profile
from eyes.eye_animator import EyeAnimator
from eyes.core.blink_engine import BlinkEngine

async def main():
    print("Halimedes Sanity Check: INITIATING")
    try:
        profile = load_eye_profile("owl04")
        hal = EyeAnimator(profile)
        blinker = BlinkEngine(hal.drawer)
    except Exception as e:
        print(f"INIT FAILURE: {e}")
        return

    print("DRAW TEST: Centered eye, no expression")
    hal.drawer.gaze_cache.clear()
    hal.set_expression("skeptical")
    hal.draw_gaze(10, 10, 1.0)
    await asyncio.sleep(1)           # ← non-blocking

    for size in ["3","0.05","3.2","0.01", "0.2", "1.4", "0.5", "1.6", "0.7", "1.8", "0.9", "1", "2"]:
        size = float(size)              
        hal.drawer.gaze_cache.clear()
        print(f"Pupil Size: {size}")
        hal.smooth_gaze(10, 10, size) 
        await asyncio.sleep(0.1)  
    await asyncio.sleep(1)           # ← non-blocking

    # start blinking in the background
    blink_task = asyncio.create_task(blinker.idle_blink_loop())
    # Example: set an initial expression
    hal.draw_gaze(10, 10, pupil=1.0)
    blinker.blink(hal.last_buf)

    for mood in ["happy","sad","angry","focused","skeptical","surprised","asleep","neutral"]:
        print(f"Setting expression: {mood}")
        try:
            await hal.set_expression(mood)
            await asyncio.sleep(2)
            for mode in ["center","left","center","right","center","up","center","down","center","wander"]:
                print(f"Gaze mode: {mode}")
                hal.apply_gaze_mode(mode)
                await asyncio.sleep(1)
        except Exception as e:
            print(f"Expression '{mood}' failed: {e}")
            break

    print("Finished sanity pass. Hal is operational.")
    # blink_task.cancel()
if __name__ == "__main__":
    asyncio.run(main())
