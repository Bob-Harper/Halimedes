# test_main.py
import asyncio
import time

from sequencers.eye_channels import GazeChannel, ExpressionChannel, BlinkChannel, ActionChannel
from sequencers.eye_behaviours  import EyeBehaviorManager
from eyes.eye_animator import EyeAnimator
from vision.face_tracking    import FaceTracker
from eyes.eye_loader   import load_eye_profile

# === replace this with one of your real ActionSequence classes ===
class DummySequence:
    def __init__(self, animator):
        self.animator = animator
        self.duration = 1.0
        self.elapsed = 0.0
        self.finished = False
    
    def update(self, dt):
        self.elapsed += dt
        # here you might call animator.direct_gaze or set_expression …
        if self.elapsed >= self.duration:
            self.finished = True


async def main():
    profile  = load_eye_profile("real_owl")
    animator = EyeAnimator(profile)
    tracker  = FaceTracker(animator)
    gaze   = GazeChannel(animator, tracker)
    expr   = ExpressionChannel(animator)
    action = ActionChannel()
    _ = BlinkChannel(animator)    
    manager = EyeBehaviorManager(gaze, expr, action)

    # start your blink loop (runs forever in background).  _ = BlinkChannel(animator)
    # BlinkChannel’s __init__ already kicked off animator.idle_blink_loop()

    # Example: set an initial expression
    expr.set_mood("happy")
    # Schedule a dummy action 2 seconds in
    asyncio.get_event_loop().call_later(
        2.0,
        lambda: action.trigger(DummySequence(animator))
    )

    prev = time.time()
    try:
        while True:
            now = time.time()
            dt  = now - prev
            prev = now

            manager.update(dt)
            await asyncio.sleep(0.016)   # ~60 fps tick
    except KeyboardInterrupt:
        print("Shutting down…")

if __name__ == "__main__":
    asyncio.run(main())
