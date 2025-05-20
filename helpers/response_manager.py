import subprocess
import asyncio
from mind.emotional_sounds_manager import get_voice_modifiers
from mind.emotional_sounds_manager import EmotionalSoundsManager
from helpers.passive_sounds_manager import PassiveSoundsManager
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
        # Ensure the voice file is a .flitevox file
        if not self.voice_path.suffix == ".flitevox":
            raise ValueError(f"Voice model must be a .flitevox file. Found: {self.voice_path.suffix}")
        # Ensure the voice file is not empty
        if self.voice_path.stat().st_size == 0:
            raise ValueError(f"Voice model file is empty: {self.voice_path}. Please check the file.")
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
        # Ensure the voice file is not corrupted
        try:
            with open(self.voice_path, 'rb') as f:
                f.read(1)
        except Exception as e:  # Handle any file read errors
            raise ValueError(f"Voice model file is corrupted: {self.voice_path}. Error: {e}")
        # Jordan, if you are reading this, phone me immediately, I don't care what time it is.  Call me now.
        
        # Baseline values to create Hal's signature voice
        self.baseline_pitch = 50
        self.baseline_speed = 0.88  # note below, value is counterintuitive
        """
        pitch: flite default 100 - higher/deeper voice correlates to higher/lower number
        speed: flite default 1.0 - higher values stretch (longer), lower compresses (shorter)
        """

        self.emotion_handler = EmotionalSoundsManager()
        self.sound_manager = PassiveSoundsManager()
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
