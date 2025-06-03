import asyncio
import random
import json
import traceback
from eyes.DrawEngine import DrawEngine
from typing import TYPE_CHECKING, Optional
if TYPE_CHECKING:
    from eyes.EyeExpressionManager import EyeExpressionManager
from eyes.EyeState import EyeState
from eyes.EyeGazeInterpolator import GazeInterpolator
from helpers.global_config import EYE_EXPRESSIONS_PATH, EYE_EXPRESSIONS_FILE
from eyes.tools.eye_maths import quantize_pupil

expressionconfig_path = EYE_EXPRESSIONS_PATH / EYE_EXPRESSIONS_FILE
if not expressionconfig_path.exists():
    raise FileNotFoundError(f"[EyeLoader] No profile named '{EYE_EXPRESSIONS_FILE}' in {EYE_EXPRESSIONS_PATH}/")
with open(expressionconfig_path, "r") as f:
    expression_map = json.load(f)
FRAME_RATE = 30
FRAME_DURATION = 1.0 / FRAME_RATE


class EyeFrameComposer:
    def __init__(self, 
                 eye_profile,
                 ):
        print("[Composer] CONSTRUCTED:", id(self))
        traceback.print_stack(limit=4)
        self.eye_profile = eye_profile
        self.expression_manager = None
        self.gaze_interpolator = None
        self.state = EyeState()
        self._previous = EyeState()
        self.drawer = DrawEngine(self.eye_profile)
        self.running = False
        self._dirty = True
        self._frame_drawn_event = asyncio.Event()

    def setup(self, gaze_interpolator, expression_manager):
        self.gaze_interpolator = gaze_interpolator
        self.expression_manager = expression_manager

    # set_eyelids directly overrides the current eyelid mask (used for blinks or tweening)
    def set_eyelids(self, lid_cfg: dict | None):
        self.state.eyelid_cfg = lid_cfg
        # print(f"[EyeFrameComposer] j6l Eyelids set to {lid_cfg}")
        self._dirty = True

    def set_gaze(self, x: int, y: int, pupil: float):
        self.state.x = int(x)
        self.state.y = int(y)
        self.state.pupil = quantize_pupil(pupil)
        self._dirty = True
        
    async def wait_for_frame(self):
        try:
            await asyncio.wait_for(self._frame_drawn_event.wait(), timeout=1)
        except asyncio.TimeoutError:
            print("[EyeFrameComposer] Warning: frame draw timed out.")

    async def start_loop(self):
        assert self.gaze_interpolator is not None, "Gaze interpolator is not set"
        assert self.expression_manager is not None, "Expression manager is not set"
        self.running = True
        while self.running:
            if self._dirty or self.state != self._previous:
                
                if random.random() < 0.05:  # ~1% chance per frame
                    if not self.expression_manager.is_blinking():
                        print("[Blink] Triggered")
                        self.expression_manager.trigger()

                # Clear the event before starting a new frame render
                self._frame_drawn_event.clear()

                # Gaze update
                self.set_gaze(self.state.x, self.state.y, self.state.pupil)
                print(f"[EyeFrameComposer] g4i Gaze set to ({self.state.x}, {self.state.y}) with pupil {self.state.pupil}")              
                # Only update expression if not blinking
                if not self.expression_manager.is_blinking():
                    self.expression_manager.update_expression()
                    # print(f"[EyeFrameComposer] f5d Expression NOT blinking, updated to {self.expression_manager.get_current_mask()}")
                else:
                    print(f"[EyeFrameComposer] h7d Expression IS BLINKING, update skipped.")                
                # Handle blink override if active
                dt = FRAME_DURATION  # ~0.016s at 60fps
                if self.expression_manager and self.expression_manager.is_blinking():
                    blink_lids = self.expression_manager.update_blink(dt)
                    if blink_lids:
                        lid_cfg = blink_lids
                        print(f"[EyeFrameComposer] Blink override active with lids: {lid_cfg}")
                    else:
                        lid_cfg = self.state.eyelid_cfg or self.expression_manager.get_mask_config()
                        print("[EyeFrameComposer] a8c No blink override, using eyelid config.")
                else:
                    lid_cfg = self.state.eyelid_cfg or self.expression_manager.get_mask_config()
                    print("[EyeFrameComposer] d3f No blink override, using eyelid config.")
                # Render the gaze frame
                left_buf, right_buf = await asyncio.to_thread(
                    self.drawer.render_gaze_frame,
                    self.state.x,
                    self.state.y,
                    self.state.pupil
                )
                # Apply lids (expression masks)
                try:
                    masked = await asyncio.to_thread(
                        self.drawer.apply_lids,
                        (left_buf, right_buf), lid_cfg
                    )
                    print("[EyeFrameComposer] e2b Lids applied successfully.")
                except Exception:
                    print("[EyeFrameComposer] Error applying lids, using unmasked buffers.")
                    masked = (left_buf, right_buf)
            
                # Display the final frame
                await asyncio.to_thread(
                    self.drawer.display,
                    masked
                )
                print("[EyeFrameComposer] Frame displayed successfully.")
                # Signal that the frame has been drawn
                self._frame_drawn_event.set()
                print("[EyeFrameComposer] Frame drawn and event set.")
            else:
                # Save the current state
                self._previous = EyeState(
                    x=self.state.x, y=self.state.y,
                    pupil=self.state.pupil,
                    expression=self.state.expression,
                    blink=self.state.blink
                )
                print("[EyeFrameComposer] No changes detected, skipping frame render.")
                self._dirty = False

            await asyncio.sleep(FRAME_DURATION)
