import random
from helpers.picrawler import Picrawler
from helpers.new_movements import NewMovements
from helpers.passive_sounds import PassiveSoundsManager
from helpers.voice_utils import speak_with_flite
import asyncio


class PassiveActionsManager:
    def __init__(self):
        self.crawler = Picrawler()
        self.passive_sound = PassiveSoundsManager()
        self.newmovements = NewMovements(self.crawler)

    async def handle_passive_actions(self, stop_event):
        """Alternate between sounds and actions while waiting for LLM response."""
        while not stop_event.is_set():
            # Weighted random choice: 70% sound, 30% action
            choice = random.choices(["sound", "action"], weights=[60, 40], k=1)[0]

            if choice == "sound":
                await self.passive_sound.sounds_thinking_loop_single()  # Play one sound
            else:
                await self.actions_thinking_loop_single()  # Perform one action

            await asyncio.sleep(1)  # Short delay before choosing again
            
    async def actions_thinking_loop_single(self):
        """Perform a single thinking action with categorized weighting."""
        speed = 85  # Default speed for actions

        # Define categorized actions
        actions_by_category = {
            "tapping": [
                self.newmovements.tap_front_right,
                self.newmovements.tap_front_left,
                self.newmovements.tap_rear_right,
                self.newmovements.tap_rear_left,
                self.newmovements.tap_all_legs,
            ],
            "standing": [
                self.newmovements.stand_tall,
                self.newmovements.sway_all_legs,
                lambda: self.crawler.do_step("stand", speed),
                lambda: self.crawler.do_step("sit", speed),
            ],
            "turning": [
                lambda: [self.crawler.do_action("turn left", 1, speed), self.crawler.do_action("turn right", 1, speed)],
                lambda: [self.crawler.do_action("turn right", 1, speed), self.crawler.do_action("turn left", 1, speed)],
            ],
            "other": [
                lambda: self.crawler.do_step("wave", speed),
                lambda: self.crawler.do_step("look_left", speed),
                lambda: self.crawler.do_step("look_right", speed),
                lambda: self.crawler.do_step("look_up", speed),
                lambda: self.crawler.do_step("look_down", speed),
                self.newmovements.sit_down
            ],
        }

        # Define weights for the categories
        category_weights = {
            "tapping": 0.4,
            "standing": 0.3,
            "turning": 0.2,
            "other": 0.1,
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
        speak_task = asyncio.create_task(speak_with_flite(words))
        wiggle_task = asyncio.create_task(self.newmovements.wiggle())

        # Ensure tasks run concurrently, but stop wiggle when speech ends
        await asyncio.gather(speak_task)  # Wait for speech task only
        wiggle_task.cancel()  # Stop wiggle after speech ends
        try:
            await wiggle_task
        except asyncio.CancelledError:
            pass

    async def shutdown_speech_actions(self, words):
        # Run speech and movement concurrently
        speak_task = asyncio.create_task(speak_with_flite(words))
        movement_task = asyncio.to_thread(self.newmovements.sit_down)
        # Wait for both tasks to complete
        await asyncio.gather(speak_task, movement_task)
        