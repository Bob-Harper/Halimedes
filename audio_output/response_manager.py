import subprocess
import asyncio
from audio_output.emotional_sounds_manager import get_voice_modifiers
from audio_output.emotional_sounds_manager import EmotionalSoundsManager
from helpers.global_config import SPEECH_MODEL_PATH, SPEECH_MODEL_NAME


class Response_Manager:
    _actions_manager = None  # Store actions manager globally

    def __init__(self, picrawler_instance, actions_manager=None, eye_animator=None):
        self.crawler = picrawler_instance
        # Hal's voicefile
        self.voice_path = SPEECH_MODEL_PATH/SPEECH_MODEL_NAME 
        # Ensure the voice file exists
        if not self.voice_path.exists():
            raise FileNotFoundError(f"Voice model not found at {self.voice_path}. Please check the path.")
        
        # Baseline values to create Hal's signature voice
        self.baseline_pitch = 50
        self.baseline_speed = 0.88  # note below, value is counterintuitive
        """
        pitch: flite default 100 - higher/deeper voice correlates to higher/lower number
        speed: flite default 1.0 - higher values stretch (longer), lower compresses (shorter)
        """

        self.emotion_handler = EmotionalSoundsManager()
        self.eye_animator = eye_animator
        # Store actions_manager once (global for this class)
        if actions_manager:
            Response_Manager._actions_manager = actions_manager  

    async def speak_with_flite(self, words, emotion="neutral"):
        """
        ** USED FOR STARTUP SEQUENCE, STATUS UPDATES, ANNOUNCEMENTS, AND COMMAND RESPONSES **
        Standalone function.
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
