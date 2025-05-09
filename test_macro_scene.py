# test_macro_scene.py
import asyncio
from eyes.eye_loader import load_eye_profile
from eyes.eye_animator import EyeAnimator
from dsl.channels import GazeChannel, ExpressionChannel  # real channels
from dsl.macro_player import MacroPlayer  # your DSL runner
from eyes.core.blink_engine import BlinkEngine


async def main():
    profile = load_eye_profile("owl04")
    animator = EyeAnimator(profile)
    blinker = BlinkEngine(animator)
    asyncio.create_task(blinker.idle_blink_loop())
    player = MacroPlayer(
        gaze=GazeChannel(animator),
        expression=ExpressionChannel(animator),
        speech=None,
        action=None
    )

    await player.run("""
        expression set mood closed
        wait 1.5
        expression set mood skeptical
        wait 1.5
        gaze move to 10 10
        wait 1.5
        gaze move to 5 5
        wait 1.5
        expression set mood happy
        wait 1.5
        gaze wandering
        wait 1.5
        expression set mood surprised
        wait 1.5
        gaze wandering
        wait 1.5
        expression set mood closed
    """)

if __name__ == "__main__":
    asyncio.run(main())
