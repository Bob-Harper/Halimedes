import time
import random

class GazeInterpolator:
    def __init__(self, animator):
        self.animator = animator  # this is EyeAnimator, to call draw_gaze()

    def smooth_transition(self, from_x, from_y, to_x, to_y, from_pupil, to_pupil, steps=8, delay=0.015):
        for i in range(1, steps + 1):
            interp_x = int(from_x + (to_x - from_x) * (i / steps))
            interp_y = int(from_y + (to_y - from_y) * (i / steps))
            raw_interp = from_pupil + (to_pupil - from_pupil) * (i / steps)
            interp_pupil = round(round(raw_interp / 0.01) * 0.01, 3)
            self.animator.draw_gaze(interp_x, interp_y, pupil=interp_pupil)
            time.sleep(delay)

    def smooth_gaze(self, to_x, to_y, to_pupil=1.0, steps=8, delay=0.015):
        state = self.animator.state
        self.smooth_transition(
            from_x=state["x"],
            from_y=state["y"],
            to_x=to_x,
            to_y=to_y,
            from_pupil=state["pupil"],
            to_pupil=to_pupil,
            steps=steps,
            delay=delay
        )

    def apply_gaze_mode(self, mode):
        modes = {
            "left": (10, 20),
            "right": (10, 0),
            "up": (20, 10),
            "down": (0, 10),
            "center": (10, 10),
            "wander": (
                random.randint(0, 20),
                random.randint(0, 20)
            )
        }
        if mode not in modes:
            print(f"[GazeInterpolator] Unknown mode: {mode}")
            return

        to_x, to_y = modes[mode]
        to_pupil = random.uniform(0.95, 1.15) if mode == "wander" else 1.0
        self.smooth_gaze(to_x, to_y, to_pupil)
