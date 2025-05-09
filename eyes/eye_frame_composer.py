import asyncio
import time
from dataclasses import dataclass
from typing import Optional

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
        self._update_event = asyncio.Event()

    def set_gaze(self, x: Optional[float] = None, y: Optional[float] = None, pupil: Optional[float] = None):
        if x is not None:
            self.state.x = x
        if y is not None:
            self.state.y = y
        if pupil is not None:
            self.state.pupil = pupil
        self._update_event.set()

    def set_expression(self, mood: str):
        self.state.expression = mood
        self._update_event.set()

    def set_blink(self, upper_lid: float, lower_lid: float):
        self.state.eyelid_upper = upper_lid
        self.state.eyelid_lower = lower_lid
        self._update_event.set()

    async def start_loop(self):
        self.running = True
        while self.running:
            async with self._lock:
                await asyncio.to_thread(
                    self.animator.draw_eye,
                    x_offset=self.state.x,
                    y_offset=self.state.y,
                    pupil_scale=self.state.pupil,
                    upper_lid=self.state.eyelid_upper,
                    lower_lid=self.state.eyelid_lower,
                    expression=self.state.expression
                )
            try:
                await asyncio.wait_for(self._update_event.wait(), timeout=FRAME_DURATION)
            except asyncio.TimeoutError:
                pass
            self._update_event.clear()

    async def stop_loop(self):
        self.running = False
        self._update_event.set()
