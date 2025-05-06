from typing import Protocol, Callable, Any
import asyncio

class Subsystem(Protocol):
    def update(self, dt: float) -> None: ...


class BehaviorSequencer:
    def __init__(
        self,
        subsystems: dict[str, Subsystem],      # <-- use Subsystem here
    ) -> None:
        self.subsystems = subsystems
        self.timeline = []  # list of (time_offset, subsystem_key, action_callable)
        self._clock = 0.0

    def schedule(
        self,
        delay: float,
        subsystem: str,
        action: Callable[[Subsystem], Any],   # action gets passed a Subsystem
    ) -> None:
        self.timeline.append((delay, subsystem, action))
        self.timeline.sort(key=lambda e: e[0])

    def start(self) -> None:
        self._clock = 0.0
        self._pending = list(self.timeline)

    async def update(self, dt: float) -> None:
        self._clock += dt

        # dispatch everything whose time has come
        while self._pending and self._pending[0][0] <= self._clock:
            _, key, action = self._pending.pop(0)
            result = action(self.subsystems[key])
            # if the action returned a coroutine, await it here
            if asyncio.iscoroutine(result):
                await result

        # then tick all subsystems (they’re still sync for gaze/blink/expr)
        for mgr in self.subsystems.values():
            maybe = mgr.update(dt)
            if asyncio.iscoroutine(maybe):
                await maybe