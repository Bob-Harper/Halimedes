import asyncio
from typing import Callable, Dict, Awaitable, Optional

# Channel interface assumptions
class GazeChannel:
    async def move_to(self, x: float, y: float, pupil: float = 1.0): ...
    async def wander(self): ...

class ExpressionChannel:
    async def set_mood(self, mood: str): ...

class SpeechChannel:
    async def speak(self, text: str): ...

class ActionChannel:
    async def perform(self, action: str): ...


class MacroPlayer:
    def __init__(self,
                 gaze: Optional[GazeChannel] = None,
                 expression: Optional[ExpressionChannel] = None,
                 speech: Optional[SpeechChannel] = None,
                 action: Optional[ActionChannel] = None):

        self.gaze = gaze
        self.expression = expression
        self.speech = speech
        self.action = action

        self.command_map: Dict[str, Callable[[str], Awaitable[None]]] = {
            'expression': self._expression,
            'gaze':       self._gaze,
            'speak':      self._speak,
            'action':     self._action,
            'wait':       self._wait,
        }

    async def run(self, script: str):
        for line in script.strip().splitlines():
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            cmd, *args = line.split()
            arg_str = ' '.join(args)
            handler = self.command_map.get(cmd)
            if handler:
                await handler(arg_str)
            else:
                print(f"[Macro] Unknown command: {cmd}")

    # --- DSL Handlers ---

    async def _expression(self, arg: str):
        if not self.expression:
            return
        if arg.startswith("set mood"):
            _, _, mood = arg.partition("set mood")
            mood = mood.strip()
            print(f"[Macro] Expression -> set mood to '{mood}'")
            await self.expression.set_mood(mood)

    async def _gaze(self, arg: str):
        if not self.gaze:
            return
        if arg.startswith("move to"):
            _, _, rest = arg.partition("move to")
            parts = rest.strip().split()
            if len(parts) >= 2:
                x, y = map(float, parts[:2])
                pupil = float(parts[2]) if len(parts) > 2 else 1.0
                print(f"[Macro] Gaze -> move to ({x}, {y}) pupil={pupil}")
                await self.gaze.move_to(x, y, pupil)
        elif arg == "wandering":
            print("[Macro] Gaze -> wandering")
            await self.gaze.wander()

    async def _speak(self, text: str):
        if self.speech:
            print(f"[Macro] Speaking: {text}")
            await self.speech.speak(text)

    async def _action(self, arg: str):
        if self.action:
            print(f"[Macro] Performing: {arg}")
            await self.action.perform(arg)

    async def _wait(self, arg: str):
        try:
            seconds = float(arg)
            print(f"[Macro] Waiting {seconds} seconds")
            await asyncio.sleep(seconds)
        except ValueError:
            print(f"[Macro] Invalid wait duration: {arg}")
