import asyncio
import random
import re
from typing import Callable, Dict, Awaitable, Optional
from dsl.channels import GazeChannel, ExpressionChannel, SpeechChannel, ActionChannel, SoundChannel
from mind.emotions_manager import EmotionCategorizer
from dsl.macro_tag_validator import MacroTagValidator

emotion_categorizer = EmotionCategorizer()


class MacroPlayer:
    def __init__(self,
                 gaze: Optional[GazeChannel] = None,
                 expression: Optional[ExpressionChannel] = None,
                 speech: Optional[SpeechChannel] = None,
                 action: Optional[ActionChannel] = None,
                 sound: Optional[SoundChannel] = None):
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

    async def _gaze(self, arg: str):
        if not self.gaze:
            return
        # Using pixel coords, not offset from center
        modes = {
            "left": (90, 100),
            "right": (100, 90),
            "up": (100, 90),
            "down": (80, 90),
            "center": (90, 90),
            "wander": (
                random.randint(80, 100),
                random.randint(80, 100)
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

            await self.gaze.move_to(x, y, pupil)

        elif arg == "wander":
            x, y = modes["wander"]
            await self.gaze.move_to(x, y, 1.0)

    async def _expression(self, arg: str):
        
        # print(f"[MacroPlayer] Received expression command: '{arg}'")
        if not self.expression:
            print("[MacroPlayer] No expression channel assigned.")
            return
        if arg.startswith("set mood"):
            _, _, mood = arg.partition("set mood")
            mood = mood.strip()
            # print(f"[MacroPlayer] Dispatching mood: {mood}")
            await self.expression.set_mood(mood)
        else:
            print(f"[MacroPlayer] Unknown expression command: {arg}")

    async def _speak(self, text: str):
        if self.speech:
            text = text.strip('"')

            # Strip <speak: ...> wrapper if present
            match = re.match(r"<speak:\s*(.*?)\s*>", text.strip(), re.IGNORECASE | re.DOTALL)

            if match:
                text = match.group(1).strip()

            # print(f"[Macro] Speaking: {text}")
            await self.speech.speak(text)

    async def _action(self, arg: str):
        if self.action:
            # print(f"[Macro] Performing: {arg}")
            await self.action.perform(arg)

    async def _sound(self, arg: str):
        if self.sound:
            # print(f"[Macro] Playing sound: {arg}")
            await self.sound.play(arg)


    async def _wait(self, arg: str):
        try:
            seconds = float(arg)
            # print(f"[Macro] Waiting {seconds} seconds")
            await asyncio.sleep(seconds)
        except ValueError:
            print(f"[Macro] Invalid wait duration: {arg}")


import re

class TagToDSL:
    @staticmethod
    def parse(text: str) -> str:
        dsl_lines = []

        # Match tags
        pattern = re.compile(r'<(\w+)>(.*?)</\1>', re.DOTALL)
        matches = pattern.findall(text)

        for tag_type, value in matches:
            tag_type = tag_type.lower().strip()
            value = value.strip()

            if tag_type == "speak":
                dsl_lines.append(f'speak "{value}"')
            elif tag_type == "gaze":
                dsl_lines.append(f'gaze move to {value}')
            elif tag_type == "face":
                dsl_lines.append(f'expression set mood {value}')
            elif tag_type == "sound":
                dsl_lines.append(f'sound {value}')
            elif tag_type == "action":
                dsl_lines.append(f'action {value}')
            else:
                print(f"[Validator] Unknown tag '{tag_type}', skipping.")

        return "\n".join(dsl_lines)
