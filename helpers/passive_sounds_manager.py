from robot_hat import Music
import asyncio
import random
import os
from helpers.global_config import SOUND_ASSETS_PATH

class PassiveSoundsManager:
    def __init__(self):
        self.music = Music() 
        self.sounds_dir = SOUND_ASSETS_PATH

    async def sounds_thinking_loop_single(self):
        """Play a single passive sound dynamically from a directory, supporting multiple file types."""
        thinking_emotion = "positive"
        sounds_positive = os.path.join(self.sounds_dir,thinking_emotion)
        supported_extensions = {".wav"}

        # Get a list of all supported sound files in the directory
        try:
            passive_sounds = [
                os.path.join(sounds_positive, file)
                for file in os.listdir(sounds_positive)
                if any(file.lower().endswith(ext) for ext in supported_extensions)
            ]
        except FileNotFoundError:
            print(f"Error: Directory '{sounds_positive}' not found.")
            return
        except Exception as e:
            print(f"Error: {e}")
            return

        if not passive_sounds:
            print(f"No supported sound files found in '{sounds_positive}'.")
            return

        # Randomly select a sound file
        sound_file = random.choice(passive_sounds)

        # Use asyncio.to_thread to call the synchronous method
        await asyncio.to_thread(self.music.sound_play, sound_file, 75)

        # Optional: Add a short delay to simulate processing time
        await asyncio.sleep(1.5)


    async def play_emotion_sound(self, emotion):
        """Play a sound corresponding to the given emotion."""
        supported_extensions = {".wav"}
        
        # Determine the directory for the given emotion
        sounds_dir = os.path.join(self.sounds_dir, emotion)
        try:
            # Collect all sound files in the emotion directory
            emotion_sounds = [
                os.path.join(sounds_dir, file)
                for file in os.listdir(sounds_dir)
                if any(file.lower().endswith(ext) for ext in supported_extensions)
            ]

            if not emotion_sounds:
                print(f"No sound files found for emotion '{emotion}'.")
                return

            # Randomly select a sound file
            sound_file = random.choice(emotion_sounds)
            # Play the sound using the Music API
            await asyncio.to_thread(self.music.sound_play, sound_file, 75)
        
        except FileNotFoundError:
            print(f"Error: Directory '{sounds_dir}' not found.")
        except Exception as e:
            print(f"Error: {e}")


    async def play_weather_intro_sound(self):
        """Play a random weather intro sound once."""
        play_announcement = "announcement"
        sounds_announcement = os.path.join(self.sounds_dir,play_announcement)
        supported_extensions = {".wav"}
        try:
            weather_intro_sounds = [
                os.path.join(sounds_announcement, file)
                for file in os.listdir(sounds_announcement)
                if any(file.lower().endswith(ext) for ext in supported_extensions)
            ]
        except FileNotFoundError:
            print(f"Error: Directory '{sounds_announcement}' not found.")
            return
        except Exception as e:
            print(f"Error: {e}")
            return

        if not weather_intro_sounds:
            print(f"No supported weather intro sounds found in '{sounds_announcement}'.")
            return

        # Select and play a random sound
        sound_file = random.choice(weather_intro_sounds)
        await asyncio.to_thread(self.music.sound_play, sound_file, 75)

    async def play_sound_indicator(self, sound_file, volume=50):
        """
        Plays a sound to indicate a state (e.g., now listening, done listening).
        Uses the robot hat's music.sound_play for playback.
        """
        try:
            await asyncio.to_thread(self.music.sound_play, sound_file, volume)
        except Exception as e:
            print(f"Error playing sound: {e}")
