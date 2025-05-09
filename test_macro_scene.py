# test_macro_scene.py

# --- MUST BE FIRST ---
from body.picrawler import Picrawler 
picrawler_instance = Picrawler()

# --- Then the rest ---
import asyncio
from eyes.eye_loader import load_eye_profile
from eyes.eye_animator import EyeAnimator
from eyes.core.blink_engine import BlinkEngine

from helpers.response_manager import Response_Manager
from helpers.passive_actions_manager import PassiveActionsManager

from dsl.channels import GazeChannel, ExpressionChannel, SpeechChannel, ActionChannel
from dsl.macro_player import MacroPlayer


async def main():
    profile = load_eye_profile("owl04")
    animator = EyeAnimator(profile)
    blinker = BlinkEngine(animator)
    asyncio.create_task(blinker.idle_blink_loop())

    # Pass single instance through all core components
    actions = PassiveActionsManager(picrawler_instance)
    response = Response_Manager(picrawler_instance, actions, animator)

    # DSL runner with ALL channels wired in
    player = MacroPlayer(
        gaze=GazeChannel(animator),
        expression=ExpressionChannel(animator),
        speech=SpeechChannel(response),
        action=ActionChannel(actions)
    )

    """
    Macro DSL Grammar:

        speak "text"
        action [subtle|expressive|full-body]
        wait [seconds]
        expression set mood [mood]
        gaze move to [x] [y]
        gaze wander

    Example:
        speak "Hello"
        expression set mood happy
        gaze move to 10 10
        wait 1.0
        action expressive
    """

    await player.run("""
        expression set mood closed
        wait 1.0
        speak "System powering up."
        expression set mood happy
        wait 1.0
        gaze move to 16 2 2
        wait 1.0
        action subtle
        wait 1.0
        speak "Servos operational."
        wait 1.0
        expression set mood skeptical
        wait 1.0
        action expressive
        wait 1.0
        action subtle
        speak "This is so exciting."
        wait 1.2
        expression set mood happy
        speak "That's enough for now."
        wait 1.0
        gaze move to 1 15 1.4
        wait 1.2
        expression set mood surprised
        wait 1.2
        gaze move to 10 10 1
        speak "Good night."
        wait 1.0
        expression set mood closed
    """)
if __name__ == "__main__":
    asyncio.run(main())
