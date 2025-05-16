import random
from body.picrawler_extended import PicrawlerExtended
from helpers.passive_sounds_manager import PassiveSoundsManager
from helpers.response_manager import Response_Manager
import asyncio


class PassiveActionsManager:
    def __init__(self, picrawler_instance):
        self.crawler = picrawler_instance
        self.passive_sound = PassiveSoundsManager()
        self.newmovements = PicrawlerExtended(self.crawler)
        self.response_manager = Response_Manager(self.crawler, self)
        self.actions_by_category = {
            "subtle": [
                ("Tap Front Right", self.newmovements.tap_front_right),
                ("Tap Front Left", self.newmovements.tap_front_left),
                ("Tap Rear Right", self.newmovements.tap_rear_right),
                ("Tap Rear Left", self.newmovements.tap_rear_left),
                ("Tap All Legs", self.newmovements.tap_all_legs),
                ("Stand Tall", self.newmovements.stand_tall),
                ("Look Left", lambda: [self.crawler.do_step(step, self.speed) for step in self.crawler.move_list["look_left"]]),
                ("Look Right", lambda: [self.crawler.do_step(step, self.speed) for step in self.crawler.move_list["look_right"]]),
                ("Sit", lambda: [self.crawler.do_step(step, self.speed) for step in self.crawler.move_list["sit"]]),
                ("Stand", lambda: [self.crawler.do_step(step, self.speed) for step in self.crawler.move_list["stand"]]),
                ("Look Up", lambda: [self.crawler.do_step(step, self.speed) for step in self.crawler.move_list["look_up"]]),
                ("Look Down", lambda: [self.crawler.do_step(step, self.speed) for step in self.crawler.move_list["look_down"]]),
                ("Wave", lambda: [self.crawler.do_step(step, self.speed) for step in self.crawler.move_list["wave"]]),
            ],
            "expressive": [
                # ("Wiggle", lambda: asyncio.create_task(self.newmovements.run_wiggle_for_seconds(3))),
                ("Pushup", lambda: self.newmovements.pushup(count=2, speed=self.speed)),
                ("Twist", lambda: self.newmovements.twist(speed=self.speed)),
                ("Handwork", lambda: self.newmovements.handwork(speed=self.speed)),
            ],
            "full-body": [
                ("Turn Left Then Forward", lambda: [
                    self.crawler.do_action("turn left angle", 1, self.speed, angle=30),
                    self.crawler.do_action("turn right angle", 1, self.speed, angle=30)
                ]),
                ("Turn Right Then Forward", lambda: [
                    self.crawler.do_action("turn right angle", 1, self.speed, angle=30),
                    self.crawler.do_action("turn left angle", 1, self.speed, angle=30)
                ]),
                ("Step Forward Then Back", lambda: [
                    self.crawler.do_action("forward", 1, self.speed),
                    self.crawler.do_action("backward", 1, self.speed)
                ]),
                ("Step Back Then Forward", lambda: [
                    self.crawler.do_action("backward", 1, self.speed),
                    self.crawler.do_action("forward", 1, self.speed)
                ]),
            ],
        }

        self.category_weights = {
            "subtle": 0.50,  # Small movements (50%)
            "expressive": 0.35,  # Bigger gestures (35%)
            "full-body": 0.15,  # Turning/walking (15%)
        }

        self.speed = 85  # Default movement speed

    async def handle_passive_actions(self, stop_event):
        """Alternate between sounds and actions while waiting for LLM response."""
        while not stop_event.is_set():
            # Weighted random choice: % sound, % action
            choice = random.choices(["sound", "action"], weights=[70, 30], k=1)[0]  # Set to Only Sounds for Debugging

            if choice == "sound":
                await self.passive_sound.sounds_thinking_loop_single()  # Play one sound
            else:
                await self.actions_thinking_loop_single()  # Perform one action

            await asyncio.sleep(1)  # Short delay before choosing again
            
    async def actions_thinking_loop_single(self):
        """Perform a single thinking action with categorized weighting."""
        # Pick a category based on weights
        category = random.choices(
            list(self.actions_by_category.keys()),
            weights=list(self.category_weights.values()),
            k=1
        )[0]
        # Pick a random action from the chosen category
        action_function = random.choice(self.actions_by_category[category])  #  Unpack the tuple

        # Execute the action
        await asyncio.to_thread(action_function)  #  Now it's actually calling a function

        # Short pause between actions
        await asyncio.sleep(1.0)


    async def startup_speech_actions(self, words):
        speak_task = asyncio.create_task(self.response_manager.speak_with_flite(words, emotion="anticipation"))
        wiggle_task = asyncio.create_task(self.newmovements.wiggle())

        # Ensure tasks run concurrently, but stop wiggle when speech ends
        await asyncio.gather(speak_task)  # Wait for speech task only
        wiggle_task.cancel()  # Stop wiggle after speech ends
        try:
            await wiggle_task
        except asyncio.CancelledError:
            pass

    async def shutdown_speech_actions(self, words):
        """Speak shutdown message, then sit down after speech completes."""
        await self.response_manager.speak_with_flite(words)  #  Speech finishes first
        await asyncio.to_thread(self.newmovements.sit_down)  #  THEN movement starts

    async def test_all_actions(self):
        """Test all actions in a sequence, announcing each before execution."""
        for category, actions in self.actions_by_category.items():
            for action_name, action in actions:
                await self.response_manager.speak_with_flite(f"Testing action: {action_name}")
                
                try:
                    if isinstance(action, list):
                        for step in action:
                            await asyncio.to_thread(step)
                    else:
                        await asyncio.to_thread(action)  # Execute movement
                    
                except Exception as e:
                    print(f"Error executing {action_name}: {e}")
                    await self.response_manager.speak_with_flite(f"Error executing {action_name}. Moving on.")
                
                await asyncio.sleep(1.0)  # Small delay between actions
        await self.response_manager.speak_with_flite("All actions tested successfully.")
