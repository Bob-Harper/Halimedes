import asyncio
from abc import ABC, abstractmethod
from typing import Optional, List, Protocol
from asyncio import Lock

from eyes.eye_animator import EyeAnimator
from vision.face_tracking import FaceTracker
from .gaze_override import GazeOverride


class ChannelSequence(Protocol):
    finished: bool
    def update(self, dt: float) -> None: ...


class BaseChannel(ABC):
    @abstractmethod
    def update(self, dt: float):
        pass


class GazeChannel(BaseChannel):
    def __init__(self,
                 animator: EyeAnimator,
                 tracker: Optional[FaceTracker] = None) -> None:
        self.animator = animator
        self.tracker = tracker
        self._overrides: List[ChannelSequence] = []
        self._lock = Lock()
        self._task = None

        if self.tracker:
            self._task = asyncio.create_task(self.tracker.track())

    async def set_gaze(self, x: float, y: float, pupil: float = 1.0) -> None:
        pupil = round(round(pupil / 0.05) * 0.05, 3)
        async with self._lock:
            await asyncio.to_thread(self.animator.smooth_gaze, x, y, pupil)

    def trigger_override(self, x: float, y: float, duration: float = 1.0) -> None:
        self._overrides.append(GazeOverride(self.animator, x, y, duration))

    def update(self, dt: float) -> None:
        if self._overrides:
            seq = self._overrides[0]
            seq.update(dt)
            if seq.finished:
                self._overrides.pop(0)

    def clear_cache(self) -> None:
        self.animator.drawer.gaze_cache.clear()


class ExpressionChannel(BaseChannel):
    def __init__(self, animator: EyeAnimator) -> None:
        self.animator = animator
        self.mood = None

    def set_mood(self, mood: str) -> None:
        self.mood = mood
        asyncio.create_task(self.animator.set_expression(mood))

    def clear_mood(self) -> None:
        self.mood = None

    def update(self, dt: float) -> None:
        pass


class BlinkChannel(BaseChannel):
    def __init__(self, engine) -> None:
        self.engine = engine
        self._task = asyncio.create_task(self.engine.idle_blink_loop())

    def update(self, dt: float) -> None:
        pass

    def blink_now(self) -> None:
        buf = self.engine.animator.last_buf
        if buf is not None:
            self.engine.blink(buf)


class ActionChannel(BaseChannel):
    def __init__(self) -> None:
        self.queue: List[ChannelSequence] = []

    def trigger(self, seq: ChannelSequence) -> None:
        self.queue.append(seq)

    def update(self, dt: float) -> None:
        if not self.queue:
            return
        current = self.queue[0]
        current.update(dt)
        if current.finished:
            self.queue.pop(0)
