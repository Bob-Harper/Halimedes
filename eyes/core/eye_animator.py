from core.draw_engine import DrawEngine

class EyeAnimator:
    def __init__(self, profile):
        self.profile = profile
        self.state = {
            "x": 10,
            "y": 10,
            "pupil": 1.0
        }
        self.drawer = DrawEngine(profile)

    def draw_gaze(self, x, y, pupil=1.0):
        self.state.update({"x": x, "y": y, "pupil": pupil})
        buf = self.drawer.generate_frame(x, y, pupil)
        self.drawer.display(buf)
