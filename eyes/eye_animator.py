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
        self.blinker = BlinkEngine(self.drawer)
        self.interpolator = GazeInterpolator(self)

    def draw_gaze(self, x, y, pupil=1.0):
        self.state.update({"x": x, "y": y, "pupil": pupil})
        buf = self.drawer.generate_frame(x, y, pupil)
        self.drawer.display(buf)
        self.last_buf = buf  # Store for blink refresh

    def blink(self):
        self.blinker.blink(self.last_buf)

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
