import asyncio
import time
import random

from eyes.eye_loader            import load_eye_profile
from eyes.eye_animator          import EyeAnimator
from eyes.core.blink_engine     import BlinkEngine
from vision.face_tracking       import FaceTracker
from sequencers.eye_channels    import GazeChannel, ExpressionChannel
from sequencers.behaviour_sequencer  import BehaviorSequencer


def rand_05(min_v: float, max_v: float) -> float:
    step = 0.05
    lo = int(min_v / step)
    hi = int(max_v / step)
    return round(random.randint(lo, hi) * step, 2)

async def main():
    # ——— SETUP ———
    profile  = load_eye_profile("owl04")
    pmin = profile.pupil_min
    pmax = profile.pupil_max
    animator = EyeAnimator(profile)
    # blinker  = BlinkEngine(animator)
    # asyncio.create_task(blinker.idle_blink_loop())
    # tracker  = FaceTracker(animator)
    # gaze_chan  = GazeChannel(animator, tracker)
    tracker  = None
    gaze_chan  = GazeChannel(animator)
    expr_chan  = ExpressionChannel(animator)
    DIRECTIONS = {
        "center": (10,10),
        "left":   ( 0,10),
        "right":  (20,10),
        "up":     (10, 0),
        "down":   (10,20),
        "wander": (
            random.randint(0, 20),
            random.randint(0, 20)
        )    }
    # ——— SEQUENCER ———
    seq = BehaviorSequencer({
        "gaze":       gaze_chan,
        "expression": expr_chan,
        # you could add "action": ActionChannel(animator) here if you have one
    })

    # schedule everything in advance (times in seconds)
    t = 0.0
    seq.schedule(t, "expression", lambda c: c.set_mood("skeptical"))
    t += 1.0
    for size in [3, 0.05, 1, 1, 1, 1]:
        seq.schedule(t, "gaze", lambda c, s=size: c.set_gaze(10, 10, rand_05(pmin, pmax)))  # Randomize on each call
        t += 0.1
    t += 1.0

    for mood in ["happy", "sad", "angry", "focused", "skeptical", "surprised", "sleepy", "neutral"]:
        seq.schedule(t, "expression", lambda c, m=mood: c.set_mood(m))
        t += 2.0

        for look in ["center", "left", "center", "right", "center", "up", "center", "down", "center", "wander"]:
            if look == "wander":
                seq.schedule(t, "gaze", lambda ch: 
                    ch.set_gaze(
                        random.randint(0, 20), 
                        random.randint(0, 20), 
                        rand_05(pmin, pmax)  # This will now be re-evaluated on each lambda execution
                    )
                )
            else:
                x,y = DIRECTIONS[look]
                seq.schedule(t, "gaze", 
                            lambda ch, x=x, y=y: ch.set_gaze(x, y, rand_05(pmin, pmax)))            
                t += 1.0

    seq.schedule(t, "expression", lambda c: c.set_mood("sleepy"))
    t += 3.0
    seq.schedule(t, "expression", lambda c: c.set_mood("closed"))

    seq.start()

    # ——— RUN LOOP ———
    prev = time.time()
    try:
        while True:
            now = time.time()
            dt  = now - prev
            prev = now

            await seq.update(dt)
            await asyncio.sleep(0.016)    # ~60 Hz
    except KeyboardInterrupt:
        pass

if __name__ == "__main__":
    asyncio.run(main())
