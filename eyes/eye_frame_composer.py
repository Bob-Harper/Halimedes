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
        self.shared_lock = asyncio.Lock()
        self.blink_engine.shared_lock = self.shared_lock 
        self._dirty = True

    def set_gaze(self, x: float, y: float, pupil: float):
        self.state.x = round(x, 3)
        self.state.y = round(y, 3)
        self.state.pupil = round(pupil, 3)
        self._dirty = True

    def set_expression(self, mood: str):
        if mood != "closed":
            self.state.expression = mood
            self._dirty = True

    async def play_blink(self):
        # Acquire lock so expression updates won't interfere
        async with self.blink_engine.shared_lock:
            current = self.state.expression or "neutral"
            current = self.state.expression or "neutral"
            await self.animator.set_expression("closed", smooth=True, steps=6, delay=0.01)
            await asyncio.sleep(0.1)
            await self.animator.set_expression(current, smooth=True, steps=6, delay=0.01)

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
                if self.blink_engine.shared_lock.locked():
                    await asyncio.sleep(0.01)
                    continue

                if self._dirty or self.state != self._previous:
                    # --- RENDER PHASE ---
                    await asyncio.to_thread(
                        self.animator.smooth_gaze,
                        x=self.state.x,
                        y=self.state.y,
                        pupil=self.state.pupil
                    )

                    async with self.shared_lock:
                        await self.animator.set_expression(self.state.expression)

                    lid_cfg = self.animator.drawer.lid_control.get_mask_config()

                    # Re-render the base gaze frame AFTER updating eyelids
                    left_buf, right_buf = await asyncio.to_thread(
                        self.animator.drawer.render_gaze_frame,
                        self.state.x,
                        self.state.y,
                        self.state.pupil
                    )
                    self.animator.last_buf = (left_buf, right_buf)

                    # Apply eyelids
                    lid_cfg = self.animator.drawer.lid_control.get_mask_config()
                    try:
                        masked = await asyncio.to_thread(
                            self.animator.drawer.apply_lids,
                            (left_buf, right_buf),
                            lid_cfg
                        )
                    except Exception as e:
                        print(f"[Composer] ERROR applying eyelids: {e}")
                        import traceback
                        traceback.print_exc()
                        masked = (left_buf, right_buf)  # Fallback: skip masking                    
                    if not masked or not all(masked):
                        print("[Composer] ERROR: Masked frame is empty or invalid.")

                    # --- DISPLAY PHASE ---
                    await asyncio.to_thread(
                        self.animator.drawer.display,
                        masked
                    )

                    # Save state
                    self._previous = EyeState(
                        x=self.state.x,
                        y=self.state.y,
                        pupil=self.state.pupil,
                        expression=self.state.expression,
                        blink=self.state.blink
                    )
                    self._dirty = False
            await asyncio.sleep(FRAME_DURATION)
