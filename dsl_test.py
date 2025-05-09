import asyncio
from eyes.eye_loader import load_eye_profile
from eyes.eye_animator import EyeAnimator
from dsl.macro_player import MacroPlayer

# --- Channels ---
async def expression_command(animator: EyeAnimator, verb: str, *args):
    if verb == "set" and args[0] == "mood":
        await animator.set_expression(args[1])

async def gaze_command(animator: EyeAnimator, verb: str, *args):
    if verb == "move" and args[0] == "to":
        x, y = map(float, args[1:3])
        animator.smooth_gaze(x, y, pupil=1.0)
    elif verb == "wandering":
        import random
        x = random.randint(0, 20)
        y = random.randint(0, 20)
        animator.smooth_gaze(x, y, pupil=1.0)

# --- Main DSL Test ---
async def main():
    profile = load_eye_profile("owl04")
    animator = EyeAnimator(profile)

    player = MacroPlayer(animator, {
        "expression": expression_command,
        "gaze": gaze_command
    })

    await player.load_and_run("""
        expression set mood skeptical
        gaze move to 10 10
        gaze move to 5 5
        expression set mood happy
        gaze wandering
        expression set mood surprised
        gaze wandering
        expression set mood closed
    """)

if __name__ == "__main__":
    asyncio.run(main())
