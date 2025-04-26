import subprocess
import asyncio
import re
import random
from helpers.emotional_sounds_manager import get_voice_modifiers
from helpers.emotional_sounds_manager import EmotionHandler
from helpers.passive_sounds_manager import PassiveSoundsManager
from helpers.global_config import SPEECH_MODEL_PATH, SPEECH_MODEL_NAME

from nltk.tokenize import sent_tokenize
from rapidfuzz import process


class Response_Manager:
    _actions_manager = None  # Store actions manager globally

    def __init__(self, picrawler_instance, actions_manager=None, eye_animator=None):
        self.crawler = picrawler_instance
        # Hal's voicefile
        self.voice_path = SPEECH_MODEL_PATH/SPEECH_MODEL_NAME 
        # Ensure the voice file exists
        if not self.voice_path.exists():
            raise FileNotFoundError(f"Voice model not found at {self.voice_path}. Please check the path.")
        # Ensure the voice file is a .flitevox file
        if not self.voice_path.suffix == ".flitevox":
            raise ValueError(f"Voice model must be a .flitevox file. Found: {self.voice_path.suffix}")
        # Ensure the voice file is not empty
        if self.voice_path.stat().st_size == 0:
            raise ValueError(f"Voice model file is empty: {self.voice_path}. Please check the file.")
        # Ensure the voice file is not corrupted
        try:
            with open(self.voice_path, 'rb') as f:
                f.read(1)
        except Exception as e:  # Handle any file read errors
            raise ValueError(f"Voice model file is corrupted: {self.voice_path}. Error: {e}")
        # Ensure the voice file is not a directory
        if self.voice_path.is_dir():
            raise ValueError(f"Voice model path is a directory: {self.voice_path}. Please check the path.")
        # Ensure the voice file is not a symlink
        if self.voice_path.is_symlink():
            raise ValueError(f"Voice model path is a symlink: {self.voice_path}. Please check the path.")
        # Ensure the voice file is not a socket
        if self.voice_path.is_socket():
            raise ValueError(f"Voice model path is a socket: {self.voice_path}. Please check the path.")
        # Ensure the voice file is not a FIFO
        if self.voice_path.is_fifo():
            raise ValueError(f"Voice model path is a FIFO: {self.voice_path}. Please check the path.")
        # Jordan, if you are reading this, phone me immediately, I don't care what time it is.  Call me now.
        
        # Baseline values to create Hal's signature voice
        self.baseline_pitch = 50
        self.baseline_speed = 0.88  # note below, value is counterintuitive
        """
        pitch: flite default 100 - higher/deeper voice correlates to higher/lower number
        speed: flite default 1.0 - higher values stretch (longer), lower compresses (shorter)
        """

        self.emotion_handler = EmotionHandler()
        self.sound_manager = PassiveSoundsManager()
        self.eye_animator = eye_animator
        # Store actions_manager once (global for this class)
        if actions_manager:
            Response_Manager._actions_manager = actions_manager  

    @classmethod
    def get_actions_manager(cls):
        """
        Fetches the stored actions manager.
        This allows accessing actions without passing it everywhere.
        """
        if cls._actions_manager is None:
            raise ValueError("Actions manager has not been initialized in Response_Manager.")
        return cls._actions_manager

    async def speak_with_flite(self, words, emotion="neutral"):
        """
        Speak using a single pitch and speed for the entire speech output.
        Baseline cadence for status, command response, and fallback processing.
        """
        # Get relative adjustment factors for pitch and speed
        emotion_settings = get_voice_modifiers(emotion)
        pitch_factor = emotion_settings["pitch_factor"]
        speed_factor = emotion_settings["speed_factor"]

        # Calculate modified pitch and speed
        pitch = int(self.baseline_pitch * pitch_factor)
        speed = round(self.baseline_speed * speed_factor, 2)

        try:
            command = [
                "flite",
                "-voice", self.voice_path,
                "--setf", f"int_f0_target_mean={pitch}",
                "--setf", f"duration_stretch={speed}",
                "-t", words,
            ]
            await asyncio.to_thread(subprocess.run, command, check=True)
        except subprocess.CalledProcessError as e:
            print(f"Error: {e}")
        except FileNotFoundError:
            print("Flite command not found. Ensure it is installed and in the PATH.")

    async def speak_with_dynamic_flite(self, full_text):
        """
        Speak with adaptive pitch and speed modulation dynamically for each 
        sentence fragment.  Speech only, does not factor for sound effects or actions.
        """
        try:
            # Step 1: Use nltk to split text into meaningful fragments (sentences/clauses)
            fragments = sent_tokenize(full_text)

            # Step 2: Process each fragment individually
            for fragment in fragments:
                # Determine the emotion for the fragment
                fragment_emotion = self.emotion_handler.analyze_text_emotion(fragment)
                emotion_settings = get_voice_modifiers(fragment_emotion)
                pitch = int(self.baseline_pitch * emotion_settings["pitch_factor"])
                speed = round(self.baseline_speed * emotion_settings["speed_factor"], 2)
                # Speak the fragment with calculated pitch and speed
                command = [
                    "flite",
                    "-voice", self.voice_path,
                    "--setf", f"int_f0_target_mean={pitch}",
                    "--setf", f"duration_stretch={speed}",
                    "-t", fragment,
                ]
                await asyncio.to_thread(subprocess.run, command, check=True)

        except Exception as e:
            print(f"Error in adaptive speech, falling back to neutral: {e}")
            # Fallback to the default flite with no modulation
            await self.speak_with_flite(full_text)

    async def fully_dynamic_response(self, full_text):
        """
        Processes an LLM-generated response, applying:
        - Emotion-based speech modulation
        - Inline sound effects
        - Inline robot actions
        """

        # Parse the response into structured parts
        processed_segments = self.process_and_replace_actions(full_text)

        for segment_type, content in processed_segments:
            if segment_type == "text":
                await self.speak_with_dynamic_flite(content)  # Speak segment

            elif segment_type == "sound":
                await self.sound_manager.play_emotion_sound(content)  # Play inline

            elif segment_type == "action":
                action_name, action_function = content  # Proper tuple unpacking
                await asyncio.to_thread(action_function)  # Perform inline

            elif segment_type == "gaze":
                await asyncio.to_thread(self.eye_animator.apply_gaze_mode, content)

            elif segment_type == "face":
                await asyncio.to_thread(self.eye_animator.set_expression, content)

            # Short delay to allow natural timing
            await asyncio.sleep(0.3)

    @staticmethod
    def remap_llm_gaze(direction):
        """
        Translate LLM directions (up/down/left/right) to match Hal's eye orientation.
        """

        # Observed behavior:
        # LLM says 'up'    => Hal looks left
        # LLM says 'right' => Hal looks up

        translation = {
            "up": "left",
            "down": "right",
            "left": "up",
            "right": "down",
            "center": "center",
            "wander": "wander"
        }

        return translation.get(direction, "center")

    def process_and_replace_actions(self, response_text):
        """
        Parses an LLM response, extracting:
        - Text for speech
        - Sound effect markers
        - Action markers
        - Keeps everything in correct order.
        """

        # Define patterns for LLM markers
        sound_effect_pattern = r"<sound effect: (.*?)>"
        action_pattern = r"<action: (.*?)>"
        gaze_pattern = r"<gaze: (.*?)>"
        face_pattern = r"<face: (.*?)>"
        # Split response text based on markers
        split_text = re.split(f"({sound_effect_pattern}|{action_pattern}|{gaze_pattern}|{face_pattern})", 
                              response_text)

        processed_segments = []
        skip_next = False  # Prevent storing extra fragments

        for i, chunk in enumerate(split_text):
            if not chunk or chunk.strip() == "":
                continue  # Ignore empty chunks

            if skip_next:
                skip_next = False  # Skip this chunk (it was an isolated marker)
                continue

            # Handle sound effects
            sound_match = re.match(sound_effect_pattern, chunk)
            if sound_match:
                effect = sound_match.group(1).strip()
                processed_segments.append(("sound", effect))
                skip_next = True  # Prevents the rogue category from getting stored
                continue  # Skip further processing for this chunk

            # Handle actions
            action_match = re.match(action_pattern, chunk)
            if action_match:
                action = action_match.group(1).strip()
                actions_manager = Response_Manager.get_actions_manager()
                action_name, action_function = Response_Manager.get_mapped_action(actions_manager, action)

                if action_function:
                    processed_segments.append(("action", (action_name, action_function)))
                    skip_next = True  # Prevents the rogue category from getting stored
                continue  # Skip further processing for this chunk

            # Gaze handling with remap
            gaze_match = re.match(gaze_pattern, chunk)
            if gaze_match:
                gaze_type = gaze_match.group(1).strip()
                remapped_gaze = self.remap_llm_gaze(gaze_type)  # <-- apply translation
                processed_segments.append(("gaze", remapped_gaze))
                skip_next = True
                continue

            # Expression handling
            face_match = re.match(face_pattern, chunk)
            if face_match:
                expr = face_match.group(1).strip()
                processed_segments.append(("face", expr))
                skip_next = True
                continue

            # If it's text and wasn't flagged for skipping, store it
            processed_segments.append(("text", chunk.strip()))

        return processed_segments
                        
    @staticmethod
    def get_mapped_action(passive_actions_manager, action_category):
        """Fetches a valid action from the closest-matching category in PassiveActionsManager."""

        #  Extract just the category names (prevent functions from being passed)
        available_categories = list(passive_actions_manager.actions_by_category.keys())
        fallback_category = "subtle"  # Default fallback

        #  Always pick the closest match
        best_match = process.extractOne(action_category, available_categories)

        matched_category = best_match[0] if best_match else fallback_category  # Ensure valid category

        #  Fetch an actual action from the chosen category
        if matched_category in passive_actions_manager.actions_by_category:
            action_name, action_function = random.choice(passive_actions_manager.actions_by_category[matched_category])
            return action_name, action_function  #  Ensure we return both!

        return None, None  # Fail-safe return

    @staticmethod
    def get_mapped_sound(sound_category):
        """Fetches the closest-matching emotion category for a sound effect."""
        
        available_folders = ["laugh", "anticipation", "surprise", "sadness", "fear", "anger"]
        fallback_folder = "disgust"  # Fallback for extreme cases

        # Always select the closest match, no confidence threshold
        best_match = process.extractOne(sound_category, available_folders)

        return best_match[0] if best_match else fallback_folder  # Always return a category name
