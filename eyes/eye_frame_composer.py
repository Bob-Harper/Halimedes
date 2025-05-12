import asyncio
import random
from dataclasses import dataclass

FRAME_RATE = 60
FRAME_DURATION = 1.0 / FRAME_RATE

@dataclass
class EyeState:
    x: int = 10             # integer only
    y: int = 10             # integer only
    pupil: float = 1.0      # float, step of 0.01
    expression: str = "neutral"  # string name only
    blink: float = 0.0      # 0.0 = open, 1.0 = fully closed

class EyeFrameComposer:
    def __init__(self, animator, expression_manager, blink_engine):
        self.expression_manager = expression_manager
        self.animator = animator
        self.blink_engine = blink_engine
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

    def set_blink(self, left: float, right: float):
        # For now, average the lid values; in future could separate
        self.state.blink = (left + right) / 2.0
        self._dirty = True

    async def play_blink(self):
        buf = self.animator.get_last_buf_safe()
        if not buf:
            print("[Blink] Warning: No last_buf available for blink.")
            return
        async for frame in self.blink_engine.blink_sequence(buf):
            self.animator.drawer.display(frame) 

    async def start_idle_blink_loop(self):
        try:
            while True:
                await asyncio.sleep(random.uniform(4, 10))
                await self.play_blink()
        except asyncio.CancelledError:
            pass

    async def start_loop(self):
        self.running = True
        while self.running:
            async with self._lock:
                if self._dirty or self.state != self._previous:
                    # --- RENDER PHASE ---
                    left_buf, right_buf = await asyncio.to_thread(
                        self.animator.drawer.render_gaze_frame,
                        self.state.x,
                        self.state.y,
                        self.state.pupil
                    )

                    # Apply eyelids based on expression and blink state
                    lid_cfg = self.animator.drawer.lid_control.get_mask_config()

                    # Re-mask with new eyelid config
                    masked = await asyncio.to_thread(
                        self.animator.drawer.apply_lids,
                        (left_buf, right_buf),
                        lid_cfg
                    )

                    # --- DISPLAY PHASE ---
                    await asyncio.to_thread(
                        self.animator.drawer.display,
                        masked
                    )

                    # --- Save previous ---
                    self._previous = EyeState(
                        x=self.state.x,
                        y=self.state.y,
                        pupil=self.state.pupil,
                        expression=self.state.expression,
                        blink=self.state.blink
                    )
                    self._dirty = False
            await asyncio.sleep(FRAME_DURATION)
