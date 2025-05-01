import asyncio
from abc import ABC, abstractmethod
from eyes.eye_animator    import EyeAnimator
from vision.face_tracking import FaceTracker
from .gaze_override import GazeOverride
from typing import Protocol, List

class ChannelSequence(Protocol):
    """Anything with an .update(dt: float) and a .finished: bool."""
    finished: bool
    def update(self, dt: float) -> None: ...


class BaseChannel(ABC):
    @abstractmethod
    def update(self, dt: float):
        pass


class GazeChannel(BaseChannel):
    def __init__(self,
                 animator: EyeAnimator,
                 tracker:   FaceTracker,
    ) -> None:
        self.animator   = animator
        self.tracker    = tracker
        self._overrides: List[ChannelSequence] = []
        # start face-tracker; it calls animator.smooth_gaze() itself
        self._task      = asyncio.create_task(self.tracker.track())

    def trigger_override(self, x: float, y: float, duration: float = 1.0) -> None:
        self._overrides.append(GazeOverride(self.animator, x, y, duration))

    def update(self, dt: float) -> None:
        if self._overrides:
            seq = self._overrides[0]
            seq.update(dt)
            if seq.finished:
                self._overrides.pop(0)
        # else: tracker is still running in background


class ExpressionChannel(BaseChannel):
    def __init__(self, animator: EyeAnimator) -> None:
        self.animator = animator
        self.mood = None

    def set_mood(self, mood: str):
        self.mood = mood
        # kick off the async lid morph
        asyncio.create_task(self.animator.smooth_transition_expression(mood))

    def clear_mood(self):
        self.mood = None

    def update(self, dt: float):
        # transition_expression handles all the work; nothing per-tick here
        pass


class BlinkChannel(BaseChannel):
    def __init__(self, engine) -> None:
        """
        engine is your real BlinkEngine(animator) instance.
        We schedule its idle_blink_loop() directly.
        """
        self.engine = engine
        self._task  = asyncio.create_task(self.engine.idle_blink_loop())

    def update(self, dt: float) -> None:
        # BlinkEngine is fully autonomous now
        pass

    def blink_now(self) -> None:
        """If you want to force-blink manually."""
        buf = self.engine.animator.last_buf
        if buf is not None:
            self.engine.blink(buf)


class ActionChannel(BaseChannel):
    def __init__(self) -> None:
        # now VS Code knows queue holds ChannelSequence objects
        self.queue: List[ChannelSequence] = []

    def trigger(self, seq: ChannelSequence) -> None:
        self.queue.append(seq)

    def update(self, dt: float) -> None:
        if not self.queue:
            return
        current = self.queue[0]
        current.update(dt)           # no more “wtf—.update() doesn’t exist”
        if current.finished:
            self.queue.pop(0)        # and .finished is known too
