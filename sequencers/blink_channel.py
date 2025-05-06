# sequencers/BlinkChannel.py
import asyncio
from eyes.core.blink_engine import BlinkEngine

class BlinkChannel:
    def __init__(self, animator):
        self.engine = BlinkEngine(animator)
        self._task  = asyncio.create_task(self.engine.idle_blink_loop())

    def update(self, dt: float):
        # blink loop is internal
        pass
