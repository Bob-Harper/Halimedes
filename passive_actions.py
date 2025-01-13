import random
from classes.picrawler import Picrawler
from classes.new_movements import NewMovements
from voice_utils import speak_with_flite
import threading

class PassiveActionsManager:
    def __init__(self):
        self.crawler = Picrawler()
        self.newmovements = NewMovements(self.crawler)

    async def actions_thinking(self):
        """Perform a random thinking action."""
        action = random.choice([
            self.newmovements.tap_front_right_async,
            self.newmovements.tap_front_left_async,
            self.newmovements.tap_rear_right_async,
            self.newmovements.tap_rear_left_async,
            self.newmovements.tap_all_legs_async,
        ])
        await action()  # Directly execute the chosen action

    async def sit_down(self):
        # Assuming these are the commands to lower the legs
        sit_down_steps = [[50, 90, 90], [50, 90, 90], [50, 90, 90], [50, 90, 90]]
        self.crawler.do_step(sit_down_steps, speed=1)
        sit_down_steps = [[50, 60, 60], [50, 60, 60], [0, 60, 60], [0, 60, 60]]
        self.crawler.do_step(sit_down_steps, speed=1)
        sit_down_steps = [[50, 30, 30], [50, 30, 30], [0, 30, 30], [0, 30, 30]]
        self.crawler.do_step(sit_down_steps, speed=1)
        sit_down_steps = [[0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0]]
        self.crawler.do_step(sit_down_steps, speed=1)


    async def wiggle(self):
        new_step = [[50, 50, -80], [50, 50, -80], [50, 50, -80], [50, 50, -80]]
        speed = 99
        for i in range(4):
            for inc in range(30, 60, 80):
                rise = [50, 50, (-80 + inc * 0.5)]
                drop = [50, 50, (-80 - inc)]
                new_step[i] = rise
                new_step[(i + 2) % 4] = drop
                new_step[(i + 1) % 4] = rise
                new_step[(i - 1) % 4] = drop
                self.crawler.do_step(new_step, speed)


    async def startup_speech_actions(self, words):
        await speak_with_flite(words)
        await self.wiggle()

    async def shutdown_speech_actions(self, words):
        await speak_with_flite(words)
        await self.sit_down()
