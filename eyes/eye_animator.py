import time 
import random
import asyncio
from .core.draw_engine import DrawEngine
from .core.blink_engine import BlinkEngine
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

    def finalize_init(self):
        """After everything loaded, finalize internal modules."""
        self.blinker = BlinkEngine(self.drawer)
        
    def draw_gaze(self, x, y, pupil=1.0):
        self.state.update({"x": x, "y": y, "pupil": pupil})
        buf = self.drawer.generate_frame(x, y, pupil)
        self.drawer.display(buf)
        self.last_buf = buf  # Store for blink refresh

    def blink(self):
        if self.blinker is None:
            print("[EyeAnimator] Warning: Blinker was missing. Auto-attaching now.")
            self.blinker = BlinkEngine(self.drawer)
        self.blinker.blink(self.last_buf)

    def dual_blink_close(self, speed=0.02):
        if self.blinker is None:
            print("[EyeAnimator] Warning: Blinker was missing. Auto-attaching now.")
            self.blinker = BlinkEngine(self.drawer)
        self.blinker.dual_blink_close(speed=speed)

    def dual_blink_open(self, pupil=1.0, x_off=0, y_off=0, speed=0.02):
        if self.blinker is None:
            print("[EyeAnimator] Warning: Blinker was missing. Auto-attaching now.")
            self.blinker = BlinkEngine(self.drawer)
        self.draw_gaze(
            self.state["x"] + x_off,
            self.state["y"] + y_off,
            pupil=pupil
        )
        if self.last_buf:
            self.blinker.dual_blink_open(self.last_buf, speed=speed)
        else:
            print("[EyeAnimator] Warning: No last_buf available for dual_blink_open")

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

    def direct_gaze(self, x, y, pupil=1.0):
        """Directly update gaze without interpolation."""
        self.state.update({"x": x, "y": y, "pupil": pupil})
        self.drawer.gaze_cache.clear()
        self.draw_gaze(x, y, pupil)

    async def idle_blink_loop(self):
        """Continuously blink at random intervals while running."""
        while True:
            wait_time = random.uniform(4, 10)  # seconds between blinks
            await asyncio.sleep(wait_time)
            if self.last_buf:
                self.blink()