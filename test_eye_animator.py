import asyncio
import random
from eyes.eye_loader import load_eye_profile
from eyes.eye_animator import EyeAnimator
from eyes.core.blink_engine import BlinkEngine

def rand_05(min_v: float, max_v: float) -> float:
    step = 0.05
    lo = int(min_v / step)
    hi = int(max_v / step)
    return round(random.randint(lo, hi) * step, 2)


async def main():
    print("Halimedes Sanity Check: INITIATING")
    # googly01, hitech13, owl01, owl02, owl03, owl04, real_owl, vector01, vector03, vector04
    #vector1 needs redone and centered better on the image file
    try:
        profile = load_eye_profile("hitech13")
        hal = EyeAnimator(profile)
        blinker = BlinkEngine(hal)
    except Exception as e:
        print(f"INIT FAILURE: {e}")
        return
    DIRECTIONS = {
        "left": (10, 20),
        "right": (10, 0),
        "up": (20, 10),
        "down": (0, 10),
        "center": (10, 10),
        "wander": (
            random.randint(0, 20),
            random.randint(0, 20)
        )    }
    print("DRAW TEST: Centered eye, no expression")
    hal.drawer.gaze_cache.clear()
    await hal.set_expression("skeptical")
    await asyncio.sleep(1)           # ← non-blocking

    for size in ["3","0.05",rand_05(0.5, 2.0),rand_05(0.5, 2.0),rand_05(0.5, 2.0),"1"]:
        size = float(size)              
        hal.drawer.gaze_cache.clear()
        print(f"Pupil Size: {size}")
        hal.smooth_gaze(10, 10, size) 
        await asyncio.sleep(0.1)  
    await asyncio.sleep(0.1)           # ← non-blocking

    # start blinking in the background
    blink_task = asyncio.create_task(blinker.idle_blink_loop())
    # Example: set an initial expression
    hal.draw_gaze(10, 10, pupil=1.0)
    blinker.blink(hal.last_buf)

    for mood in ["test","test2","angry","surprised","sleepy"]:
        print(f"Setting expression: {mood}")
        await hal.set_expression(mood)
        try:
            await asyncio.sleep(0.2)
            for mode in ["center","left","center","right","center","up","center","down","center","wander"]:
                print(f"Gaze mode: {mode}")
                if mode == "wander":
                    hal.smooth_gaze(
                        random.randint(0,20), 
                        random.randint(0,20), 
                        rand_05(0.5, 2.0), 
                    )
                else:
                    x,y = DIRECTIONS[mode]
                    hal.smooth_gaze(x, y, rand_05(0.5, 2.0))
                await asyncio.sleep(0.1)
        except Exception as e:
            print(f"Expression '{mood}' failed: {e}")
            break

    print("Finished sanity pass. Hal is operational.")
    await hal.set_expression("closed")
    await asyncio.sleep(1)           # ← non-blocking


    blink_task.cancel()
if __name__ == "__main__":
    asyncio.run(main())
