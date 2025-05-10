import asyncio
import time
from dataclasses import dataclass, field

FRAME_RATE = 60
FRAME_DURATION = 1.0 / FRAME_RATE

@dataclass
class EyeState:
    x: float = 10.0
    y: float = 10.0
    pupil: float = 1.0
    eyelid_upper: float = 0.0
    eyelid_lower: float = 0.0
    expression: str = "neutral"

class EyeFrameComposer:
    def __init__(self, animator):
        self.animator = animator
        self.state = EyeState()
        self._previous = EyeState()
        self.running = False
        self._lock = asyncio.Lock()
        self._dirty = True

    def set_gaze(self, x: float, y: float, pupil: float):
        self.state.x = round(x, 3)
        self.state.y = round(y, 3)
        self.state.pupil = round(pupil, 3)
        self._dirty = True

    def set_expression(self, mood: str):
        if mood != self.state.expression:
            self.state.expression = mood
            self._dirty = True

    def set_blink(self, upper_lid: float, lower_lid: float):
        if (upper_lid != self.state.eyelid_upper or lower_lid != self.state.eyelid_lower):
            self.state.eyelid_upper = upper_lid
            self.state.eyelid_lower = lower_lid
            self._dirty = True

    async def start_loop(self):
        self.running = True
        while self.running:
            async with self._lock:
                if self._dirty or self.state != self._previous:
                    await asyncio.to_thread(self.animator.draw_eye,
                        x_offset=self.state.x,
                        y_offset=self.state.y,
                        pupil_scale=self.state.pupil,
                        upper_lid=self.state.eyelid_upper,
                        lower_lid=self.state.eyelid_lower,
                        expression=self.state.expression
                    )
                    self._previous = EyeState(
                        x=self.state.x,
                        y=self.state.y,
                        pupil=self.state.pupil,
                        eyelid_upper=self.state.eyelid_upper,
                        eyelid_lower=self.state.eyelid_lower,
                        expression=self.state.expression
                    )
                    self._dirty = False
            await asyncio.sleep(FRAME_DURATION)

    async def stop_loop(self):
        self.running = False
