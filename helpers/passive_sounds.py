from robot_hat import Music
import asyncio
import random
import os


class PassiveSoundsManager:
    def __init__(self):
        self.music = Music()  # def sound_play(self, filename, volume=None)


    async def sounds_thinking_loop_single(self):
        """Play a single passive sound dynamically from a directory, supporting multiple file types."""
        # Define the directory containing the sound files
        sounds_dir = "/home/msutt/hal/sounds/passive/positive"
        
        # List of supported file extensions
        supported_extensions = {".wav"}

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


    async def play_emotion_sound(self, emotion):
        """Play a sound corresponding to the given emotion."""
        # List of supported file extensions
        supported_extensions = {".wav"}
        
        # Determine the directory for the given emotion
        sounds_dir = os.path.join(self.sounds_base_dir, emotion)
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
            print(f"Playing sound for emotion '{emotion}': {sound_file}")  # Debugging message

            # Play the sound using the Music API
            await asyncio.to_thread(self.music.sound_play, sound_file, 75)
        
        except FileNotFoundError:
            print(f"Error: Directory '{sounds_dir}' not found.")
        except Exception as e:
            print(f"Error: {e}")


    async def play_weather_intro_sound(self):
        """Play a random weather intro sound once."""
        sounds_dir = "/home/msutt/hal/sounds/passive/announcement"  # Directory for weather intro sounds
        supported_extensions = {".wav"}
        try:
            weather_intro_sounds = [
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

        if not weather_intro_sounds:
            print(f"No supported weather intro sounds found in '{sounds_dir}'.")
            return

        # Select and play a random sound
        sound_file = random.choice(weather_intro_sounds)
        print(f"Playing weather intro sound: {sound_file}")  # Debug message
        await asyncio.to_thread(self.music.sound_play, sound_file, 75)


    async def play_sound_indicator(self, sound_file, volume=75):
        """
        Plays a sound to indicate a state (e.g., now listening, done listening).
        Uses the robot hat's music.sound_play for playback.
        """
        from robot_hat import music  # Import if not already in your scope
        
        try:
            print(f"Playing sound: {sound_file} at volume {volume}")
            await asyncio.to_thread(self.music.sound_play, sound_file, volume)
        except Exception as e:
            print(f"Error playing sound: {e}")    