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
    def __init__(self, animator, expression_manager):
        self.expression_manager = expression_manager
        self.animator = animator
        self.state = EyeState()
        self._previous = EyeState()
        self.running = False
        self._lock = asyncio.Lock()
        self.blink_override = asyncio.Event()
        self.blink_override.clear()   # Normal mode by default        
        self._dirty = True

    def set_gaze(self, x: int, y: int, pupil: float):
        self.state.x = round(x, 3)
        self.state.y = round(y, 3)
        self.state.pupil = round(pupil, 3)
        self._dirty = True

    async def set_expression(self, mood: str):
        if mood == "closed":
            return  # Only blink uses “closed”

        # If a blink is mid‑flight, wait for it to finish (blink_override cleared)
        while self.blink_override.is_set():
            await asyncio.sleep(0.005)

        # Now it’s safe to change the expression
        self.state.expression = mood
        self._dirty = True

    async def play_blink(self):
        # Signal “blink in progress”
        self.blink_override.set()
        try:
            current = self.state.expression
            await self.animator.set_expression("closed", smooth=True, steps=6, delay=0.01)
            await asyncio.sleep(0.1)
            await self.animator.set_expression(current, smooth=True, steps=6, delay=0.01)
        finally:
            # Always clear, even if blink fails
            self.blink_override.clear()
    
    async def start_idle_blink_loop(self):
        try:
            while True:
                await asyncio.sleep(random.uniform(8, 12))
                await self.play_blink()
        except asyncio.CancelledError:
            pass

    async def start_loop(self):
        self.running = True
        while self.running:
            async with self._lock:
                if self._dirty or self.state != self._previous:
                    # --- GAZE PHASE (no lock needed) ---
                    await asyncio.to_thread(
                        self.animator.smooth_gaze,
                        x=self.state.x, y=self.state.y, pupil=self.state.pupil
                    )

                    # --- EXPRESSION PHASE (lock only around expression) ---
                    if not self.blink_override.is_set():
                        await self.animator.set_expression(self.state.expression)

                    # --- RENDER PHASE (no lock) ---
                    lid_cfg = self.animator.drawer.lid_control.get_mask_config()
                    left_buf, right_buf = await asyncio.to_thread(
                        self.animator.drawer.render_gaze_frame,
                        self.state.x, self.state.y, self.state.pupil
                    )
                    self.animator.last_buf = (left_buf, right_buf)

                    # --- EYE‑LID MASK PHASE (no lock) ---
                    try:
                        masked = await asyncio.to_thread(
                            self.animator.drawer.apply_lids,
                            (left_buf, right_buf), lid_cfg
                        )
                    except Exception:
                        masked = (left_buf, right_buf)

                    # --- DISPLAY PHASE (no lock) ---
                    await asyncio.to_thread(
                        self.animator.drawer.display, masked
                    )

                    # Save state snapshot
                    self._previous = EyeState(
                        x=self.state.x, y=self.state.y,
                        pupil=self.state.pupil,
                        expression=self.state.expression,
                        blink=self.state.blink
                    )
                    self._dirty = False
            await asyncio.sleep(FRAME_DURATION)
