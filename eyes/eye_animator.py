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
        
    def draw_gaze(self, x, y, pupil=1.0):
        self.state.update({"x": x, "y": y, "pupil": pupil})
        buf = self.drawer.generate_frame(x, y, pupil)
        self.drawer.display(buf)
        self.last_buf = buf  # Store for blink refresh

    def apply_gaze_mode(self, mode):
        self.interpolator.apply_gaze_mode(mode)

    def smooth_gaze(self, x, y, pupil=1.0):
        self.interpolator.smooth_gaze(x, y, pupil)

    def set_expression(self, mood):
        self.drawer.lid_control.set_expression(mood)
        self.drawer.gaze_cache.clear()
        self.draw_gaze(
            self.state["x"],
            self.state["y"],
            pupil=self.state["pupil"]
        )

    def transition_expression(self, mood, speed=0.02):
        self.set_expression(mood)
        buf = self.drawer.generate_frame(
            x_off=self.state["x"],
            y_off=self.state["y"],
            pupil_size=self.state["pupil"]
        )

        self.blinker.dual_blink_close(speed)
        self.blinker.dual_blink_open(buf, speed)

    async def smooth_transition_expression(self, mood, steps=20, delay=0.02):
        """Smoothly transition from current eyelid positions to new expression over multiple frames."""
        target = self.drawer.lid_control.expression_map.get(mood)
        if not target:
            print(f"[EyeAnimator] Unknown expression '{mood}'")
            return

        # Determine start and end positions
        current = self.drawer.lid_control.lids.copy()

        for step in range(1, steps + 1):
            intermediate = {}

            # Gradually interpolate each lid value
            for lid in ['top', 'bottom', 'left', 'right']:
                start_value = current.get(lid, 0)
                end_value = target.get(lid, start_value)
                interpolated_value = start_value + (end_value - start_value) * (step / steps)
                intermediate[lid] = int(interpolated_value)

            # Apply this intermediate lid config
            self.drawer.lid_control.lids.update(intermediate)
            buf = self.drawer.generate_frame(
                x_off=self.state["x"],
                y_off=self.state["y"],
                pupil_size=self.state["pupil"]
            )
            self.drawer.display(buf)
            self.last_buf = buf

            await asyncio.sleep(delay)  # Short pause to allow human eye to see animation
