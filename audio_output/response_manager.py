import subprocess
import asyncio
import tempfile
from audio_output.emotional_sounds_manager import get_voice_modifiers
from audio_output.emotional_sounds_manager import EmotionalSoundsManager
from helpers.global_config import SPEECH_MODEL_PATH, SPEECH_MODEL_NAME
import soundfile as sf
import numpy as np


class Response_Manager:
    _actions_manager = None  # Store actions manager globally

    def __init__(self, picrawler_instance, actions_manager=None, eye_animator=None, internal_state=None, working_memory=None):
        self.working_memory = working_memory
        self._speech_lock = asyncio.Lock()
        self._current_speech_task = None
        self.internal_state = internal_state
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
        Speak using Flite with emotion-based pitch/speed,
        writing to a temp WAV and playing it.
        """
        if not words:
            return
        print(f"[TTS] Speaking with emotion '{emotion}': {words}")  # Debug print
        # Get relative adjustment factors for pitch and speed
        emotion_settings = get_voice_modifiers(emotion)
        pitch_factor = emotion_settings["pitch_factor"]
        speed_factor = emotion_settings["speed_factor"]

        # Calculate modified pitch and speed
        pitch = int(self.baseline_pitch * pitch_factor)
        speed = round(self.baseline_speed * speed_factor, 2)

        # Create a temp WAV file
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=True) as tmp:
            wav_path = tmp.name

            flite_cmd = [
                "flite",
                "-voice", str(self.voice_path),
                "--setf", f"int_f0_target_mean={pitch}",
                "--setf", f"duration_stretch={speed}",
                "-t", words,
                "-o", wav_path,
            ]

            try:
                # Run flite to synthesize speech
                await asyncio.to_thread(
                    subprocess.run,
                    flite_cmd,
                    check=True
                )

                play_cmd = ["aplay", wav_path]
                await asyncio.to_thread(
                    subprocess.run,
                    play_cmd,
                    check=True
                )
                if self.internal_state:
                    self.internal_state.is_speaking = False
            except subprocess.CalledProcessError as e:
                print(f"[TTS] Flite/aplay error: {e}")
                if self.internal_state:
                    self.internal_state.is_speaking = False
            except FileNotFoundError as e:
                print(f"[TTS] Command not found: {e}")
                if self.internal_state:
                    self.internal_state.is_speaking = False

    async def speak(self, text, emotion="neutral", interrupt=False):
        if interrupt and self._current_speech_task and not self._current_speech_task.done():
            self._current_speech_task.cancel()
            try:
                await self._current_speech_task
            except asyncio.CancelledError:
                if self.internal_state:
                    self.internal_state.is_speaking = False
                pass
        if self.internal_state:
            self.internal_state.is_speaking = True
        self._current_speech_task = asyncio.create_task(
            self._speak_serialized(text, emotion)
        )
        if self.internal_state:
            self.internal_state.is_speaking = False

    async def _speak_serialized(self, text, emotion):
        async with self._speech_lock:
            await self.speak_with_flite(text, emotion)

        # Append assistant turn AFTER speech actually happened
        if self.working_memory is not None:
            self.working_memory.add("assistant", text)

        if self.internal_state:
            self.internal_state.is_speaking = False


    async def say(self, text):
        return await self.speak_with_flite(text, emotion="neutral")


if __name__ == "__main__":
    import asyncio

    async def main():
        rm = Response_Manager(
            picrawler_instance=None,
            actions_manager=None,
            eye_animator=None,
            internal_state=None
        )

        # Text you want HAL to say
        test_line = """
The quick brown fox jumps over the lazy dog
How vexingly quick daft zebras jump
The five boxing wizards jump quickly.
Waltz, bad nymph, for quick jigs vex.
        """


        await rm.speak_with_flite(test_line, emotion="positive")

    asyncio.run(main())

"""
emotion_voice_map = {
    "joy": {"pitch_factor": 1.4, "speed_factor": 0.7},       # Higher pitch, faster speech
    "positive": {"pitch_factor": 1.3, "speed_factor": 0.8},  # Energetic and faster
    "neutral": {"pitch_factor": 1.0, "speed_factor": 1.0},   # Baseline voice
    "trust": {"pitch_factor": 1.15, "speed_factor": 0.9},    # Warm, steady, and slightly faster
    "surprise": {"pitch_factor": 1.5, "speed_factor": 0.6},  # Very excited and fast
    "fear": {"pitch_factor": 0.6, "speed_factor": 1.1},      # Low pitch, slower—hesitant
    "anger": {"pitch_factor": 0.5, "speed_factor": 1.15},     # Deep, intense, and slower
    "sadness": {"pitch_factor": 0.4, "speed_factor": 1.25},   # Very slow and low pitch
    "disgust": {"pitch_factor": 0.6, "speed_factor": 1.2},   # Low pitch, slower pace
    "anticipation": {"pitch_factor": 1.25, "speed_factor": 0.75}, # Faster and eager
    "negative": {"pitch_factor": 0.5, "speed_factor": 1.15},  # Deep pitch, slower
    "announcment": {"pitch_factor": 0.85, "speed_factor": 1.1},  # Neutral, slower
}

phrases for testing
The birch canoe slid on the smooth planks.
Glue the sheet to the dark blue background.
It's easy to tell the depth of a well.
These days a chicken leg is a rare dish.
Rice is often served in round bowls.
The juice of lemons makes fine punch.
The box was thrown beside the parked truck.
The hogs were fed chopped corn and garbage.
Four hours of steady work faced us.
A large size in stockings is hard to sell.

"""
