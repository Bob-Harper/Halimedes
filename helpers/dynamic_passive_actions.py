import random
from helpers.picrawler import Picrawler
from helpers.new_movements import NewMovements
from helpers.passive_sounds import PassiveSoundsManager
from helpers.response_utils import Response_Manager
import asyncio
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk import pos_tag


class PassiveActionsManager:
    def __init__(self):
        self.crawler = Picrawler()
        self.passive_sound = PassiveSoundsManager()
        self.newmovements = NewMovements(self.crawler)
        self.response_manager = Response_Manager()


    async def handle_passive_actions(self, stop_event):
        """Alternate between sounds and actions while waiting for LLM response."""
        while not stop_event.is_set():
            # Weighted random choice: 70% sound, 30% action
            # choice = random.choices(["sound", "action"], weights=[60, 40], k=1)[0]
            choice = random.choices(["sound", "action"], weights=[100, 0], k=1)[0]  # Set to Only Sounds for Debugging


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
        # Run speech and movement concurrently
        speak_task = asyncio.create_task(self.response_manager.speak_with_flite(words))
        movement_task = asyncio.to_thread(self.newmovements.sit_down)
        # Wait for both tasks to complete
        await asyncio.gather(speak_task, movement_task)
        
    async def process_and_replace_actions(self, response_text):
        """
        Detects full sentences describing sounds or actions, and dynamically replaces them.
        Returns the modified conversational text and the list of detected actions/sounds.
        """
        sentences = sent_tokenize(response_text)
        modified_text = ""
        detected_events = []

        for sentence in sentences:
            words = word_tokenize(sentence)
            tagged_words = pos_tag(words)

            # Detect if the sentence describes a sound effect
            if any(word.lower() in self.sound_keywords for word, tag in tagged_words):
                detected_events.append(("sound", sentence))
                # print(f"Detected sound description: {sentence}")
                continue  # Skip adding this sentence to the spoken text

            # Detect if the sentence describes an action
            if any(word.lower() in self.action_keywords for word, tag in tagged_words):
                detected_events.append(("action", sentence))
                print(f"Detected action description: {sentence}")
                continue  # Skip adding this sentence to the spoken text

            # Otherwise, keep the sentence as part of the spoken text
            modified_text += sentence + " "

        return modified_text.strip(), detected_events    
    
    def extract_sound_type(self, description):
        """
        Extracts the key sound keyword from the sentence.
        """
        for word in word_tokenize(description):
            if word.lower() in self.sound_keywords:
                return word.lower()  # Return the detected sound keyword
        return "default_sound"  # Fallback if no keyword is found

    def extract_action_type(self, description):
        """
        Extracts the key action phrase from the sentence.
        """
        words = word_tokenize(description)
        for i, (word, tag) in enumerate(pos_tag(words)):
            if word.lower() in self.action_keywords:
                return ' '.join(words[i:i + 3])  # Return 3-word action phrase
        return "default_action"  # Fallback if no action phrase is found

def passive_wave(robot):
    print("[DEBUG] Triggering passive wave")
    return robot.wave()

def passive_look_left(robot):
    print("[DEBUG] Triggering passive look left")
    return robot.look_left()

def passive_look_right(robot):
    print("[DEBUG] Triggering passive look right")
    return robot.look_right()
