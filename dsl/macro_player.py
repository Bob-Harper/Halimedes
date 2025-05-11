import asyncio
import random
import re
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
                 action: Optional[ActionChannel] = None,
                 sound: Optional[Callable[[str], Awaitable[None]]] = None):

        self.gaze = gaze
        self.expression = expression
        self.speech = speech
        self.action = action
        self.sound = sound

        self.command_map: Dict[str, Callable[[str], Awaitable[None]]] = {
            'expression': self._expression,
            'gaze':       self._gaze,
            'speak':      self._speak,
            'action':     self._action,
            'sound':      self._sound,
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

        if arg.startswith("move to"):
            _, _, rest = arg.partition("move to")
            parts = rest.strip().split()

            # If symbolic direction like "left"
            if len(parts) == 1 and parts[0] in modes:
                x, y = modes[parts[0]]
                pupil = 1.0
            # If full manual coordinates
            elif len(parts) >= 2:
                x, y = map(float, parts[:2])
                pupil = float(parts[2]) if len(parts) > 2 else 1.0
            else:
                print(f"[Macro] Invalid gaze args: {parts}")
                return

            print(f"[Macro] Gaze -> move to ({x}, {y}) pupil={pupil}")
            await self.gaze.move_to(x, y, pupil)

        elif arg == "wander":
            x, y = modes["wander"]
            print(f"[Macro] Gaze -> wander ({x}, {y}) pupil=1.0")
            await self.gaze.move_to(x, y, 1.0)

    async def _speak(self, text: str):
        if self.speech:
            text = text.strip('"')
            print(f"[Macro] Speaking: {text}")
            await self.speech.speak(text)

    async def _action(self, arg: str):
        if self.action:
            print(f"[Macro] Performing: {arg}")
            await self.action.perform(arg)

    async def _sound(self, arg: str):
        if self.sound:
            print(f"[Macro] Playing sound: {arg}")
            await self.sound.play(arg)


    async def _wait(self, arg: str):
        try:
            seconds = float(arg)
            print(f"[Macro] Waiting {seconds} seconds")
            await asyncio.sleep(seconds)
        except ValueError:
            print(f"[Macro] Invalid wait duration: {arg}")


class TagToDSL:
    TAG_PATTERNS = {
        "sound": re.compile(r"<sound effect:\s*(\w+)>", re.IGNORECASE),
        "action": re.compile(r"<action:\s*(\w+)>", re.IGNORECASE),
        "gaze": re.compile(r"<gaze:\s*(\w+)>", re.IGNORECASE),
        "face": re.compile(r"<face:\s*(\w+)>", re.IGNORECASE),
        "speak": re.compile(r"<speak:\s*(.*?)>", re.IGNORECASE),
    }

    @staticmethod
    def parse(text: str) -> str:
        lines = text.strip().split("\n")
        dsl_lines = []
        for line in lines:
            line = line.strip()
            if not line:
                continue
            match_found = False
            for kind, pattern in TagToDSL.TAG_PATTERNS.items():
                m = pattern.fullmatch(line)
                if m:
                    arg = m.group(1).strip()
                    if kind == "sound":
                        dsl_lines.append(f"sound {arg}")
                    elif kind == "action":
                        dsl_lines.append(f"action {arg}")
                    elif kind == "gaze":
                        if arg == "wander":
                            dsl_lines.append("gaze wander")
                        else:
                            dsl_lines.append(f"gaze move to {arg}")
                    elif kind == "face":
                        dsl_lines.append(f"expression set mood {arg}")
                    elif kind == "speak":
                        dsl_lines.append(f'speak "{arg}"')
                    match_found = True
                    break
            if not match_found:
                dsl_lines.append(f'speak "{line}"')
        return "\n".join(dsl_lines)
