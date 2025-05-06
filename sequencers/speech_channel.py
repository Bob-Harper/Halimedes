# sequencers/speech_channel.py
import asyncio
from abc import ABC, abstractmethod

class BaseChannel(ABC):
    @abstractmethod
    def update(self, dt: float) -> None:
        ...

class SpeechChannel(BaseChannel):
    def __init__(self, response_manager):
        self._rm    = response_manager
        self._queue: list[tuple[str, dict]] = []
        self._busy = False

    def trigger(self, text: str, **flite_kwargs):
        """
        Queue a simple flite announcement.
        flite_kwargs can include emotion="happy", etc.
        """
        self._queue.append((text, flite_kwargs))

    def update(self, dt: float) -> None:
        # if we're already speaking, wait
        if self._busy or not self._queue:
            return

        text, kw = self._queue.pop(0)
        # mark busy, then speak and clear busy when done
        self._busy = True

        async def _speak_and_clear():
            await self._rm.speak_with_flite(text, **kw)
            self._busy = False

        asyncio.create_task(_speak_and_clear())
