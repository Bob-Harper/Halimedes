import asyncio
import random
from typing import Callable


class GazeChannel:
    def __init__(self, gaze_interpolator, pmin=0.8, pmax=1.3):
        self.gaze_interpolator = gaze_interpolator
        self.pmin = pmin
        self.pmax = pmax

    async def move_to(self, x: float, y: float, pupil: float = 1.0):
        pupil = round(round(pupil / 0.05) * 0.05, 3)
        await self.gaze_interpolator.interpolate_gaze(x, y, pupil, steps=20, delay=0.01)

    async def wander(self):
        x = random.randint(80, 100)
        y = random.randint(80, 100)
        pupil = self.rand_05(self.pmin, self.pmax)
        await self.gaze_interpolator.interpolate_gaze(x, y, pupil, steps=20, delay=0.01)

    @staticmethod
    def rand_05(min_v: float, max_v: float) -> float:
        step = 0.05
        lo = int(min_v / step)
        hi = int(max_v / step)
        return round(random.randint(lo, hi) * step, 2)


class ExpressionChannel:
    def __init__(self, expression_manager):
        self.expression_manager = expression_manager

    async def set_mood(self, mood: str):
        print(f"[ExpressionChannel] set_mood called with: {mood}")
        self.expression_manager.set_expression(mood)


class SoundChannel:
    def __init__(self, play_sound_func: Callable[[str], None]):
        self.play_sound = play_sound_func

    async def play(self, sound: str):
        await asyncio.to_thread(self.play_sound, sound)


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

        if action in self.actions.actions_by_category:
            name, fn = random.choice(self.actions.actions_by_category[action])
            await asyncio.to_thread(fn)
        else:
            for cat in self.actions.actions_by_category.values():
                for name, fn in cat:
                    if name.lower() == action:
                        await asyncio.to_thread(fn)
                        return
            print(f"[WARN] Unknown action: '{action}'")
