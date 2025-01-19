from time import sleep
from robot_hat import Music
import asyncio
import random
import os


class PassiveSoundsManager:
    def __init__(self):
        self.music = Music()  # def sound_play(self, filename, volume=None)

    async def oldsounds_thinking_loop_single(self):
        """Play a single passive sound."""
        passive_sounds = [
            "/home/msutt/hal/sounds/bell.wav",
            "/home/msutt/hal/sounds/depress.wav",
            "/home/msutt/hal/sounds/depress2.wav",
            "/home/msutt/hal/sounds/happy2.wav",
            "/home/msutt/hal/sounds/sign.wav",
            "/home/msutt/hal/sounds/talk1.wav",
            "/home/msutt/hal/sounds/talk3.wav",
            "/home/msutt/hal/sounds/vigilance.wav",
        ]
        sound_file = random.choice(passive_sounds)

        # Use asyncio.to_thread to call the synchronous method
        await asyncio.to_thread(self.music.sound_play, sound_file, 75)

        # Optional: Add a short delay to simulate processing time
        await asyncio.sleep(1.5)

    async def sounds_thinking_loop_single(self):
        """Play a single passive sound dynamically from a directory, supporting multiple file types."""
        # Define the directory containing the sound files
        sounds_dir = "/home/msutt/hal/sounds/passive"
        
        # List of supported file extensions
        supported_extensions = {".wav", ".mp3", ".ogg", ".flac", ".aac"}
        
        # Get a list of all supported sound files in the directory
        try:
            passive_sounds = [
                os.path.join(sounds_dir, file)
                for file in os.listdir(sounds_dir)
                if any(file.lower().endswith(ext) for ext in supported_extensions)
            ]
        except FileNotFoundError:
            print(f"Error: Directory '{sounds_dir}' not found.")
            return
        except Exception as e:
            print(f"Error: {e}")
            return

        if not passive_sounds:
            print(f"No supported sound files found in '{sounds_dir}'.")
            return

        # Randomly select a sound file
        sound_file = random.choice(passive_sounds)

        # Use asyncio.to_thread to call the synchronous method
        await asyncio.to_thread(self.music.sound_play, sound_file, 75)

        # Optional: Add a short delay to simulate processing time
        await asyncio.sleep(1.5)

