import time 
import asyncio
from .core.draw_engine import DrawEngine
from .core.gaze_interpolator import GazeInterpolator


class EyeAnimator:
    def __init__(self, profile):
        self.profile = profile
        self.state = {
            "x": 10,
            "y": 10,
            "pupil": 1.0
        }
        self.drawer = DrawEngine(profile)
        self.blinker = None  # <-- initially empty
        self.interpolator = GazeInterpolator(self)
        from eyes.dualeye_driver import eye_left, eye_right
        for eye in (eye_left, eye_right):
            eye.fill_screen(0x0000)  # clear both displays black
        time.sleep(0.1)  # short SPI bus stabilization
        self.drawer.gaze_cache.clear()  # clear the gaze cache
        self.last_buf = None  # clear the last buffer for blinking
        self.current_expression = None  # track what’s live now
        
    def draw_gaze(self, x, y, pupil=1.0):
        self.state.update({"x": x, "y": y, "pupil": pupil})
        left_buf, right_buf = self.drawer.render_gaze_frame(x, y, pupil)
        self.drawer.display((left_buf, right_buf))
        self.last_buf = (left_buf, right_buf)

    def apply_gaze_mode(self, mode):
        self.interpolator.apply_gaze_mode(mode)

    def smooth_gaze(self, x, y, pupil=1.0):
        self.interpolator.smooth_gaze(x, y, pupil)

    async def set_gaze_safely(self, x, y, pupil):
        await asyncio.to_thread(self.smooth_gaze, x, y, pupil)        

    async def set_expression(self, mood: str, smooth: bool = None):
        """
        Public API: switch to `mood`.  
        If `smooth` is True, always tween; if False, always snap;  
        if None (default), auto-decide: snap on first call, tween thereafter.

        examples:
        # “Perform for the audience” instantly:
        await hal.set_expression("neutral")

        # Later, do a polished cross-fade:
        await hal.set_expression("surprised")    # smooth auto

        # If you have to reset quickly (no tween):
        await hal.set_expression("neutral", smooth=False)
        """
        do_smooth = smooth
        if do_smooth is None:
            # first time or resetting?
            do_smooth = (self.current_expression is not None 
                         and self.current_expression != mood)

        if do_smooth:
            await self._smooth_expression(mood)
        else:
            self._instant_expression(mood)

    async def _smooth_expression(self, mood: str, steps=20, delay=0.02):
        """
        Tween from the current expression corners to the new `mood`.
        """
        expr_map = self.drawer.lid_control.expression_map
        target   = expr_map.get(mood)
        if not target:
            print(f"[EyeAnimator] Unknown expression '{mood}'")
            return

        start_cfg = self.drawer.lid_control.lids.copy()
        for step in range(1, steps + 1):
            frac = step / steps
            interp_cfg = {}
            for corner in (
                "eye1_top_left","eye1_top_right",
                "eye1_bottom_left","eye1_bottom_right",
                "eye2_top_left","eye2_top_right",
                "eye2_bottom_left","eye2_bottom_right"
                ):
                s = start_cfg.get(corner, 0)
                e = target.get(corner, s)
                interp_cfg[corner] = int(s + (e - s) * frac)

            self.drawer.lid_control.lids.update(interp_cfg)
            self.drawer.gaze_cache.clear()

            # <-- same unpacking here
            left_buf, right_buf = self.drawer.render_gaze_frame(
                self.state["x"],
                self.state["y"],
                pupil_size=self.state["pupil"]
            )
            self.drawer.display((left_buf, right_buf))
            self.last_buf = (left_buf, right_buf)

            await asyncio.sleep(delay)

        self.current_expression = mood

    def _instant_expression(self, mood: str):
        """
        Immediately snap to `mood`—no tween.
        """
        self.drawer.lid_control.set_expression(mood)
        self.drawer.gaze_cache.clear()

        # <-- this used to be buf = generate_frame(...)
        left_buf, right_buf = self.drawer.render_gaze_frame(
            self.state["x"],
            self.state["y"],
            pupil_size=self.state["pupil"]
        )
        # now display both eyes at once
        self.drawer.display((left_buf, right_buf))

        # stash for blink
        self.last_buf = (left_buf, right_buf)
        self.current_expression = mood
        self.current_expression = mood
        