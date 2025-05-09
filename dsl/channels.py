import asyncio
import random

class GazeChannel:
    def __init__(self, animator):
        self.animator = animator

    async def move_to(self, x: float, y: float, pupil: float = 1.0):
        pupil = round(round(pupil / 0.05) * 0.05, 3)
        await asyncio.to_thread(self.animator.smooth_gaze, x, y, pupil)

    async def wander(self):
        x = random.randint(0, 20)
        y = random.randint(0, 20)
        pupil = round(random.uniform(0.6, 1.4), 2)
        await self.move_to(x, y, pupil)


class ExpressionChannel:
    def __init__(self, animator):
        self.animator = animator

    async def set_mood(self, mood: str):
        await self.animator.set_expression(mood)


class SpeechChannel:
    def __init__(self, synth):
        self.synth = synth

    async def speak(self, text: str):
        await asyncio.to_thread(self.synth.say, text)


class ActionChannel:
    def __init__(self, driver):
        self.driver = driver

    async def perform(self, action: str):
        await asyncio.to_thread(self.driver.execute, action)
