import random
from helpers.picrawler import Picrawler
from helpers.new_movements import NewMovements
from helpers.sound_effects import PassiveSoundsManager
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
            choice = random.choices(["sound", "action"], weights=[70, 30], k=1)[0]

            if choice == "sound":
                print("Playing a sound...")  # Debug
                await self.passive_sound.sounds_thinking_loop_single()  # Play one sound
            else:
                print("Performing an action...")  # Debug
                await self.actions_thinking_loop_single()  # Perform one action

            await asyncio.sleep(1)  # Short delay before choosing again
            
    async def actions_thinking_loop_single(self):
        """Perform a single thinking action."""
        actions = [
            self.newmovements.tap_front_right,
            self.newmovements.tap_front_left,
            self.newmovements.tap_rear_right,
            self.newmovements.tap_rear_left,
            self.newmovements.tap_all_legs,
        ]
        weights = [0.3, 0.3, 0.15, 0.15, 0.1]  # Adjust probabilities
        action = random.choices(actions, weights=weights)[0]
        
        # Use asyncio.to_thread to execute the sync action
        await asyncio.to_thread(action)
        
        # Short pause between actions
        await asyncio.sleep(1.0)

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
        """Perform a smooth wiggle motion."""
        new_step = [[50, 50, -80], [50, 50, -80], [50, 50, -80], [50, 50, -80]]
        speed = 99

        while True:  # Continuous loop, can be broken externally if needed
            for i in range(4):  # Cycle through legs
                for inc in range(30, 60, 80):  # Increment rise/drop values
                    rise = [50, 50, (-80 + inc * 0.5)]
                    drop = [50, 50, (-80 - inc)]
                    new_step[i] = rise
                    new_step[(i + 2) % 4] = drop
                    new_step[(i + 1) % 4] = rise
                    new_step[(i - 1) % 4] = drop
                    await asyncio.to_thread(self.crawler.do_step, new_step, speed)
                    await asyncio.sleep(0.05)  # Small delay for smoother animation

    async def startup_speech_actions(self, words):
        speak_task = asyncio.create_task(speak_with_flite(words))
        wiggle_task = asyncio.create_task(self.wiggle())

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
        movement_task = asyncio.create_task(self.sit_down())
        # Wait for both tasks to complete
        await asyncio.gather(speak_task, movement_task)
