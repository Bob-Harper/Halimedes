import asyncio
import random
from eyes.eye_loader import load_eye_profile



class GazeChannel:
    def __init__(self, animator):
        self.animator = animator
        profile  = load_eye_profile("owl04")
        self.pmin = profile.pupil_min
        self.pmax = profile.pupil_max

    async def move_to(self, x: float, y: float, pupil: float = 1.0):
        pupil = round(round(pupil / 0.05) * 0.05, 3)
        await asyncio.to_thread(self.animator.smooth_gaze, x, y, pupil)

    async def wander(self):
        x = random.randint(0, 20)
        y = random.randint(0, 20)
        pupil = self.rand_05(self.pmin, self.pmax)
        await self.move_to(x, y, pupil)

    def rand_05(self, min_v: float, max_v: float) -> float:
        step = 0.05
        lo = int(min_v / step)
        hi = int(max_v / step)
        return round(random.randint(lo, hi) * step, 2)


class ExpressionChannel:
    def __init__(self, animator):
        self.animator = animator

    async def set_mood(self, mood: str):
        await self.animator.set_expression(mood)


class SpeechChannel:
    def __init__(self, response_manager):
        self.response_manager = response_manager

    async def speak(self, text: str):
        await self.response_manager.speak_with_flite(text)



class ActionChannel:
    def __init__(self, action_manager):
        self.actions = action_manager

    async def perform(self, action: str):
        action = action.lower().strip()

        # Check if it's a known category (subtle, expressive, full-body)
        if action in self.actions.actions_by_category:
            name, fn = random.choice(self.actions.actions_by_category[action])
            await asyncio.to_thread(fn)
        else:
            # Try to find an individual action by name
            for cat in self.actions.actions_by_category.values():
                for name, fn in cat:
                    if name.lower() == action:
                        await asyncio.to_thread(fn)
                        return
            print(f"[WARN] Unknown action: '{action}'")
