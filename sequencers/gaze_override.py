# sequencers/gaze_override.py
from eyes.eye_animator import EyeAnimator
from typing import Protocol

# Reuse your protocol so type‐checkers stay happy
class ChannelSequence(Protocol):
    finished: bool
    def update(self, dt: float) -> None: ...

class GazeOverride:
    def __init__(
        self,
        animator: EyeAnimator,
        x: float,
        y: float,
        duration: float = 1.0,
    ) -> None:
        self.animator = animator
        self.x = x
        self.y = y
        self.duration = duration
        self.elapsed = 0.0
        self.finished = False

    def update(self, dt: float) -> None:
        # immediate jump — swap to smooth_gaze() if you want a transition
        self.animator.direct_gaze(self.x, self.y)
        self.elapsed += dt
        if self.elapsed >= self.duration:
            self.finished = True
