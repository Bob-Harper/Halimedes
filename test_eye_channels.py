import asyncio
import time

from eyes.eye_loader            import load_eye_profile
from eyes.eye_animator          import EyeAnimator
from eyes.core.blink_engine     import BlinkEngine
from vision.face_tracking       import FaceTracker
from sequencers.eye_channels    import GazeChannel, ExpressionChannel, BlinkChannel
from sequencers.behaviour_sequencer  import BehaviorSequencer

async def main():
    # ——— SETUP ———
    profile  = load_eye_profile("owl04")
    animator = EyeAnimator(profile)
    tracker  = FaceTracker(animator)
    blinker  = BlinkEngine(animator)

    gaze_chan  = GazeChannel(animator, tracker)
    expr_chan  = ExpressionChannel(animator)
    blink_chan = BlinkChannel(blinker)    # fire & forget blink loop

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
    # pupil sweep (we’ll just nudge gaze around with same pupil size)
    for size in [3, .05, 3.2, .01, 2, .033, 1]:
        seq.schedule(t, "gaze", lambda c, s=size: c.update(0) or c.animator.smooth_gaze(10, 10, s))
        t += 0.1
    t += 1.0

    # then the big expression<->gaze dance
    for mood in ["happy","sad","angry","focused","skeptical","surprised","asleep","neutral"]:
        seq.schedule(t, "expression", lambda c, m=mood: c.set_mood(m))
        t += 2.0
        for mode in ["center","left","center","right","center","up","center","down","center","wander"]:
            seq.schedule(t, "gaze", lambda c, m=mode: c.apply_gaze_mode(m))
            t += 1.0

    seq.start()

    # ——— RUN LOOP ———
    prev = time.time()
    try:
        while True:
            now = time.time()
            dt  = now - prev
            prev = now

            seq.update(dt)
            await asyncio.sleep(0.016)    # ~60 Hz
    except KeyboardInterrupt:
        pass

if __name__ == "__main__":
    asyncio.run(main())
