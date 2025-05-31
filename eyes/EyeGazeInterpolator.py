from typing import TYPE_CHECKING, Optional
if TYPE_CHECKING:
    from eyes.EyeFrameComposer import EyeFrameComposer
from eyes.tools.eye_maths import quantize_pupil
import asyncio
import random


class GazeInterpolator:
    def __init__(self,
                 composer: Optional['EyeFrameComposer'] = None
                 ):
        self.composer = composer

    async def smooth_gaze(self, x, y, pupil=1.0):
        await self.interpolate_gaze(x, y, pupil)

    async def interpolate_gaze(self, to_x, to_y, to_pupil=1.0, steps=20, delay=0.01):
        assert self.composer is not None, "Composer must be set before interpolating gaze"
        from_x, from_y, from_pupil = (
            self.composer.state.x,
            self.composer.state.y,
            self.composer.state.pupil
        )
        for i in range(1, steps + 1):
            frac = i / steps
            interp_x = int(from_x + (to_x - from_x) * frac)
            interp_y = int(from_y + (to_y - from_y) * frac)
            interp_pupil = quantize_pupil(from_pupil + (to_pupil - from_pupil) * frac)
            self.composer.set_gaze(interp_x, interp_y, interp_pupil)
            self._dirty = True
            await self.composer.wait_for_frame()
            await asyncio.sleep(delay)
