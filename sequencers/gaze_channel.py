# sequencers/GazeChannel.py
import asyncio
from vision.face_tracking import FaceTracker
from eyes.eye_animator    import EyeAnimator
from typing import Protocol, Optional

class Channel(Protocol):
    def update(self, dt: float) -> None: ...

class GazeChannel(Channel):
    def __init__(self, animator: EyeAnimator, tracker: Optional[FaceTracker]):
        self.animator = animator
        self._task = asyncio.create_task(tracker.track())

    def update(self, dt: float):
        # nothing here—tracker loop drives gaze
        pass


    def set_gaze(self, x: float, y: float, pupil: float = 1.0):
        # schedule the blocking smooth_gaze in a worker thread
        asyncio.create_task(
            asyncio.to_thread(self.animator.smooth_gaze, x, y, pupil)
        )