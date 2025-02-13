import random
import asyncio
from helpers.picrawler import Picrawler
from helpers.new_movements import NewMovements
from helpers.passive_sounds import PassiveSoundsManager
from helpers.response_utils import Response_Manager


class PassiveActionsManager:
    def __init__(self):
        self.crawler = Picrawler()
        self.passive_sound = PassiveSoundsManager()
        self.newmovements = NewMovements(self.crawler)
        self.response_manager = Response_Manager()

    async def handle_passive_actions(self, stop_event):
        """Alternate between sounds and actions while waiting for LLM response."""
        while not stop_event.is_set():
            # 60% Sound, 40% Action
            choice = random.choices(["sound", "action"], weights=[0, 100], k=1)[0]

            if choice == "sound":
                await self.passive_sound.sounds_thinking_loop_single() 
            else:
                await self.actions_thinking_loop_single()

            await asyncio.sleep(1)

    async def actions_thinking_loop_single(self):
        """Perform a single thinking action with categorized weighting."""
        speed = 85  # Default movement speed

        # Define categorized actions
        actions_by_category = {
            "subtle": [
                self.newmovements.tap_front_right,
                self.newmovements.tap_front_left,
                self.newmovements.tap_rear_right,
                self.newmovements.tap_rear_left,
                self.newmovements.tap_all_legs,
                self.newmovements.stand_tall,
                lambda: self.crawler.do_step("sit", speed),
                lambda: self.crawler.do_step("stand", speed),
                lambda: self.crawler.do_step("look_left", speed),
                lambda: self.crawler.do_step("look_right", speed),
                lambda: self.crawler.do_step("look_up", speed),
                lambda: self.crawler.do_step("look_down", speed),
                lambda: self.crawler.do_step("wave", speed),
                lambda: self.newmovements.glance(direction="left", angle=25, speed=speed),
                lambda: self.newmovements.glance(direction="right", angle=25, speed=speed),
                lambda: self.newmovements.glance(direction="forward", angle=25, speed=speed),
                lambda: self.newmovements.glance(direction="left", angle=25, speed=speed),
                lambda: self.newmovements.glance(direction="forward", angle=25, speed=speed),
                lambda: self.newmovements.glance(direction="right", angle=25, speed=speed),
                lambda: self.newmovements.glance(direction="forward", angle=25, speed=speed),
            ],
            "expressive": [
                lambda: self.newmovements.wiggle(duration=3),  # Wiggle for 3 sec
                lambda: self.newmovements.pushup(count=3, speed=speed),  # 3x pushups
                lambda: self.newmovements.swimming(count=3, speed=speed),  # 3x swimming
                lambda: self.newmovements.twist(speed=speed),
                lambda: self.newmovements.handwork(speed=speed),
            ],
            "full-body": [
                lambda: [self.crawler.do_action("turn left angle", 1, speed, angle=30),
                         self.crawler.do_action("turn right angle", 1, speed, angle=30)],  # Reset after turn
                lambda: [self.crawler.do_action("turn right angle", 1, speed, angle=30),
                         self.crawler.do_action("turn left angle", 1, speed, angle=30)],  # Reset after turn
                lambda: [self.crawler.do_action("forward", 1, speed),
                         self.crawler.do_action("backward", 1, speed)],  # Reset after walk
                lambda: [self.crawler.do_action("backward", 1, speed),
                         self.crawler.do_action("forward", 1, speed)],  # Reset after walk
            ],
        }

        # Define probability weights for categories
        category_weights = {
            "subtle": 0.50,  # Small movements (50%)
            "expressive": 0.35,  # Bigger gestures (35%)
            "full-body": 0.15,  # Turning/walking (15%)
        }

        # Pick a category based on weights
        category = random.choices(list(actions_by_category.keys()), weights=category_weights.values(), k=1)[0]

        # Pick a random action from the chosen category
        action = random.choice(actions_by_category[category])

        # Execute the action
        await asyncio.to_thread(action)

        # Short pause between actions
        await asyncio.sleep(1.0)

    async def startup_speech_actions(self, words):
        """Speech + wiggle during startup."""
        speak_task = asyncio.create_task(self.response_manager.speak_with_flite(words, emotion="anticipation"))
        wiggle_task = asyncio.create_task(self.newmovements.wiggle())

        # Ensure tasks run concurrently, but stop wiggle when speech ends
        await asyncio.gather(speak_task)
        wiggle_task.cancel()
        try:
            await wiggle_task
        except asyncio.CancelledError:
            pass

    async def shutdown_speech_actions(self, words):
        """Sit down while speaking shutdown phrase."""
        speak_task = asyncio.create_task(self.response_manager.speak_with_flite(words))
        movement_task = asyncio.to_thread(self.newmovements.sit_down)

        await asyncio.gather(speak_task, movement_task)
