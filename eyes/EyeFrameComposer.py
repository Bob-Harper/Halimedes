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
FRAME_RATE = 60
FRAME_DURATION = 1.0 / FRAME_RATE


class EyeFrameComposer:
    def __init__(self, eye_profile):
        # print("[Composer] CONSTRUCTED:", id(self))
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
        # print(f"[Composer] Setup called with gaze_interpolator={id(gaze_interpolator)}, expression_manager={id(expression_manager)}")
        self.gaze_interpolator = gaze_interpolator
        self.expression_manager = expression_manager

    def set_eyelids(self, lid_cfg: dict | None):
        # print(f"[Composer] set_eyelids called with: {lid_cfg}")
        self.state.eyelid_cfg = lid_cfg
        self._dirty = True

    def set_gaze(self, x: int, y: int, pupil: float):
        # print(f"[Composer] set_gaze called with x={x}, y={y}, pupil={pupil}")
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
        # print("[Composer] start_loop entered")
        while self.running:
            if self._dirty or self.state != self._previous:
                # print("[Composer] State dirty or changed, proceeding with frame update")
                if random.random() < 0.05:
                    if not self.expression_manager.is_blinking():
                        # print("[Blink] Triggered")
                        self.expression_manager.trigger()

                self._frame_drawn_event.clear()

                self.set_gaze(self.state.x, self.state.y, self.state.pupil)
                # print(f"[Composer] Current Gaze: ({self.state.x}, {self.state.y}) Pupil: {self.state.pupil}")

                if not self.expression_manager.is_blinking():
                    # print("[Composer] Updating expression (not blinking)")
                    self.expression_manager.update_expression()
                else:
                    print("[Composer] Skipping expression update (blinking)")

                dt = FRAME_DURATION
                if self.expression_manager and self.expression_manager.is_blinking():
                    blink_lids = self.expression_manager.update_blink(dt)
                    if blink_lids:
                        lid_cfg = blink_lids
                        # print(f"[Composer] Blink override active. Using lids: {lid_cfg}")
                    else:
                        lid_cfg = self.state.eyelid_cfg or self.expression_manager.get_mask_config()
                        # print("[Composer] Blink override ended. Falling back to expression lids.")
                else:
                    lid_cfg = self.state.eyelid_cfg or self.expression_manager.get_mask_config()
                    # print("[Composer] No blink override. Using expression lids.")

                # print(f"[Composer] Frame eyelids set to: {lid_cfg}")

                left_buf, right_buf = await asyncio.to_thread(
                    self.drawer.render_gaze_frame,
                    self.state.x,
                    self.state.y,
                    self.state.pupil
                )

                try:
                    masked = await asyncio.to_thread(
                        self.drawer.apply_lids,
                        (left_buf, right_buf), lid_cfg
                    )
                    # print("[Composer] Lids applied successfully.")
                except Exception as e:
                    # print(f"[Composer] Error applying lids: {e}. Using unmasked buffers.")
                    masked = (left_buf, right_buf)

                await asyncio.to_thread(self.drawer.display, masked)
                # print("[Composer] Frame displayed successfully.")
                self._frame_drawn_event.set()
                # print("[Composer] Frame event set.")

            else:
                # print("[Composer] No changes detected. Skipping frame update.")
                self._previous = EyeState(
                    x=self.state.x, y=self.state.y,
                    pupil=self.state.pupil,
                    expression=self.state.expression,
                    blink=self.state.blink
                )
                self._dirty = False

            await asyncio.sleep(FRAME_DURATION)
