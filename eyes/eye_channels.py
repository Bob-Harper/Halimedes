# eyes/eye_channels.py

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
        await self.expression_manager.animate_expression(mood)
