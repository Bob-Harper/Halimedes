import asyncio
from eyes.eye_loader   import load_eye_profile
from eyes.eye_animator import EyeAnimator, BlinkEngine
from vision.face_tracking import FaceTracker

async def main():
    profile  = load_eye_profile("real_owl")
    animator = EyeAnimator(profile)
    animator.blinker = BlinkEngine(animator.drawer)
    asyncio.create_task(animator.idle_blink_loop())
    await animator.smooth_transition_expression("neutral")

    tracker = FaceTracker(animator)
    await tracker.track()

if __name__ == "__main__":
    asyncio.run(main())
