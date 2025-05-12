import asyncio
import random

class BlinkEngine:
    def __init__(self, composer):
        self.composer = composer
        self._task = None
        self._running = False

    async def idle_blink_loop(self):
        self._running = True
        try:
            while self._running:
                await asyncio.sleep(8.0)  # average blink every 6s
                await self.blink()
        except asyncio.CancelledError:
            pass

    async def blink(self):
        await self._close_lids()
        await asyncio.sleep(0.1)
        await self._open_lids()

    async def _close_lids(self):
        self.composer.set_blink(1.0, 1.0)

    async def _open_lids(self):
        self.composer.set_blink(0.0, 0.0)

    async def stop(self):
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass


class GazeChannel:
    def __init__(self, composer, pmin=0.8, pmax=1.3):
        self.composer = composer
        self.pmin = pmin
        self.pmax = pmax

    async def move_to(self, x: float, y: float, pupil: float = 1.0):
        pupil = round(round(pupil / 0.05) * 0.05, 3)
        self.composer.set_gaze(x, y, pupil)

    async def wander(self):
        x = random.randint(0, 20)
        y = random.randint(0, 20)
        pupil = self.rand_05(self.pmin, self.pmax)
        await self.move_to(x, y, pupil)

    @staticmethod
    def rand_05(min_v: float, max_v: float) -> float:
        step = 0.05
        lo = int(min_v / step)
        hi = int(max_v / step)
        return round(random.randint(lo, hi) * step, 2)


class ExpressionChannel:
    def __init__(self, composer):
        self.composer = composer

    async def set_mood(self, mood: str):
        self.composer.set_expression(mood)


class SoundChannel:
    def __init__(self, play_sound_func):
        self.play_sound = play_sound_func

    async def play(self, sound: str):
        await asyncio.to_thread(self.play_sound, sound)


class SpeechChannel:
    def __init__(self, response_manager):
        self.response_manager = response_manager

    async def speak(self, text: str):
        await self.response_manager.speak_with_flite(text)


class ActionChannel:
    def __init__(self, action_manager):
        self.actions = action_manager

    async def perform(self, action: str):
        action = action.lower().strip()

        if action in self.actions.actions_by_category:
            name, fn = random.choice(self.actions.actions_by_category[action])
            await asyncio.to_thread(fn)
        else:
            for cat in self.actions.actions_by_category.values():
                for name, fn in cat:
                    if name.lower() == action:
                        await asyncio.to_thread(fn)
                        return
            print(f"[WARN] Unknown action: '{action}'")

