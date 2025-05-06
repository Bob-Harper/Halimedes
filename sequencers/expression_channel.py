# sequencers/ExpressionChannel.py
import asyncio
from eyes.eye_animator import EyeAnimator

class ExpressionChannel:
    def __init__(self, animator: EyeAnimator):
        self.animator = animator

    def set_mood(self, mood: str):
        asyncio.create_task(self.animator.set_expression(mood))

    def update(self, dt: float):
        # expressions are async—no per-tick work
        pass
