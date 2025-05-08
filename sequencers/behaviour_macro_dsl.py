# sequencers/behavior_macro_dsl.py
# A minimal DSL + scheduler interpreter for behavior macros

import asyncio
from typing import Callable, Coroutine, Union

Command = tuple[str, list[Union[str, float]]]
ActionFunc = Callable[..., Union[None, Coroutine]]


class BehaviorMacroRunner:
    def __init__(self, subsystems: dict[str, Callable[[str, float], Coroutine]]):
        self.subsystems = subsystems

    async def run_macro(self, macro: str) -> None:
        """
        Run a string-defined macro. Example:
        """
        lines = [line.strip() for line in macro.strip().splitlines() if line.strip() and not line.startswith("#")]

        for line in lines:
            parts = line.split()
            if len(parts) < 2:
                print(f"[Macro] Invalid command: {line}")
                continue

            channel, action = parts[0], parts[1]
            args = [self._parse_arg(arg) for arg in parts[2:]]

            if channel not in self.subsystems:
                print(f"[Macro] Unknown channel: {channel}")
                continue

            try:
                await self.subsystems[channel](action, *args)
            except Exception as e:
                print(f"[Macro] Error on line '{line}': {e}")

    def _parse_arg(self, arg: str) -> Union[float, str]:
        try:
            return float(arg)
        except ValueError:
            return arg


# Example stub interface for the subsystems (you would use actual channel logic)
async def gaze_command(action: str, *args):
    if action == "move":
        x, y = args[:2]
        print(f"Gaze -> move to ({x}, {y})")
        await asyncio.sleep(0.1)
    elif action == "wander":
        print("Gaze -> wandering")
        await asyncio.sleep(0.2)


async def expression_command(action: str, *args):
    print(f"Expression -> set mood to '{action}'")
    await asyncio.sleep(0.1)


async def main():
    runner = BehaviorMacroRunner({
        "gaze": gaze_command,
        "expression": expression_command,
    })

    demo_macro = """
        # This is a macro sequence
        expression skeptical
        gaze move 10 10
        gaze move 5 5
        expression happy
        gaze wander
    """
    await runner.run_macro(demo_macro)


if __name__ == "__main__":
    asyncio.run(main())
