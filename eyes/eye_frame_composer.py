
import asyncio
import time
from dataclasses import dataclass

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
        self.running = False
        self._lock = asyncio.Lock()

    def set_gaze(self, x: float, y: float, pupil: float):
        self.state.x = x
        self.state.y = y
        self.state.pupil = pupil

    def set_expression(self, mood: str):
        self.state.expression = mood

    def set_blink(self, upper_lid: float, lower_lid: float):
        self.state.eyelid_upper = upper_lid
        self.state.eyelid_lower = lower_lid

    async def start_loop(self):
        self.running = True
        while self.running:
            async with self._lock:
                self.animator.draw_eye(
                    x_offset=self.state.x,
                    y_offset=self.state.y,
                    pupil_scale=self.state.pupil,
                    upper_lid=self.state.eyelid_upper,
                    lower_lid=self.state.eyelid_lower,
                    expression=self.state.expression
                )
            await asyncio.sleep(FRAME_DURATION)

    async def stop_loop(self):
        self.running = False
