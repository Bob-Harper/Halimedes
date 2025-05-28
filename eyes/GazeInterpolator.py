from eyes.EyeFrameComposer import EyeFrameComposer, EyeState
from eyes.tools.eye_maths import quantize_pupil
import asyncio
import random
from typing import Optional


class GazeInterpolator:
    def __init__(self,
                 composer: Optional['EyeFrameComposer'] = None
                 ):
        self.state = EyeState()
        self.composer = composer

    def set_gaze(self, x: int, y: int, pupil: float):
        self.state.x = int(x)
        self.state.y = int(y)
        self.state.pupil = quantize_pupil(pupil)
        self._dirty = True

    async def smooth_gaze(self, x, y, pupil=1.0):
        await self.interpolate_gaze(x, y, pupil)

    async def interpolate_gaze(self, to_x, to_y, to_pupil=1.0, steps=20, delay=0.01):
        assert self.composer is not None, "Composer must be set before interpolating gaze"
        from_x, from_y, from_pupil = self.state.x, self.state.y, self.state.pupil

        for i in range(1, steps + 1):
            frac = i / steps
            interp_x = int(from_x + (to_x - from_x) * frac)
            interp_y = int(from_y + (to_y - from_y) * frac)
            interp_pupil = quantize_pupil(from_pupil + (to_pupil - from_pupil) * frac)

            self.set_gaze(interp_x, interp_y, interp_pupil)
            self._dirty = True
            await self.composer.wait_for_frame()
            await asyncio.sleep(delay)

    async def translate_gaze_mode(self, mode):
        modes = {
            "left": (10, 20),
            "right": (10, 0),
            "up": (20, 10),
            "down": (0, 10),
            "center": (10, 10),
            "wander": (
                random.randint(0, 20),
                random.randint(0, 20)
            )
        }
        if mode not in modes:
            print(f"[GazeInterpolator] Unknown mode: {mode}")
            return

        to_x, to_y = modes[mode]
        to_pupil = 1.0
        await self.interpolate_gaze(to_x, to_y, to_pupil)
        