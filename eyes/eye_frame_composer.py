import asyncio
from dataclasses import dataclass

FRAME_RATE = 60
FRAME_DURATION = 1.0 / FRAME_RATE

@dataclass
class EyeState:
    x: int = 10             # integer only
    y: int = 10             # integer only
    pupil: float = 1.0      # float, step of 0.01
    expression: str = "neutral"  # string name only

class EyeFrameComposer:
    def __init__(self, animator, expression_manager, blinker):
        self.expression_manager = expression_manager
        self.animator = animator
        self.blinker = blinker
        self.state = EyeState()
        self._previous = EyeState()
        self.running = False
        self._lock = asyncio.Lock()
        self._dirty = True

    def set_gaze(self, x: float, y: float, pupil: float):
        self.state.x = round(x, 3)
        self.state.y = round(y, 3)
        self.state.pupil = round(pupil, 3)
        self._dirty = True

    def set_expression(self, mood: str):
        if mood != self.state.expression:
            self.state.expression = mood
            self._dirty = True

    def set_blink(self):
            self._dirty = True

    async def start_loop(self):
        print("Eye frame loop started.")
        self.running = True
        print("Eye frame self.running = " + str(self.running))
        while self.running:
            async with self._lock:
                if self._dirty or self.state != self._previous:
                    print("Drawing new eye frame...")

                    await asyncio.to_thread(self.animator.smooth_gaze,
                        x=self.state.x,
                        y=self.state.y,
                        pupil=self.state.pupil
                    )

                    await asyncio.to_thread(self.expression_manager.draw_expression,
                        expression=self.state.expression
                    )

                    self._previous = EyeState(
                        x=self.state.x,
                        y=self.state.y,
                        pupil=self.state.pupil,
                        expression=self.state.expression
                    )
                    self._dirty = False
            await asyncio.sleep(FRAME_DURATION)
