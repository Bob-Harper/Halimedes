#!/usr/bin/env python3
from .basic import _Basic_class
from .utils import is_installed, run_command
from distutils.spawn import find_executable
import asyncio
import os
import re

class TTS(_Basic_class):
    """Text to speech class using Flite"""

    FLITE = 'flite'  # Define Flite as the engine

    def __init__(self, voice_path, duration_stretch=1.0, pitch=120, *args, **kwargs):
        """
        Initialize the TTS class with configurable parameters.

        :param voice_path: Path to the Flite voice file.
        :type voice_path: str
        :param duration_stretch: Stretch factor for duration, controls cadence.
        :type duration_stretch: float
        :param pitch: Target pitch (fundamental frequency).
        :type pitch: int
        """
        super().__init__()
        self.voice_path = voice_path
        self.duration_stretch = duration_stretch
        self.pitch = pitch
        self.engine = self.FLITE

        # Check if Flite is installed
        if not is_installed(self.FLITE):
            raise Exception("TTS engine: flite is not installed.")

    def _check_executable(self, executable):
        """Check if a given executable is available on the system."""
        executable_path = find_executable(executable)
        return executable_path is not None

    def sanitize_text(self, words):
        """
        Remove or replace characters that are problematic for shell commands or file names.
        We allow alphanumeric characters, spaces, and single quotes.
        """
        sanitized = re.sub(r"[^\w\s']", '', words)  # Allow alphanumeric, spaces, and single quotes
        sanitized = sanitized.strip()  # Remove leading/trailing whitespace
        return sanitized  # No escaping of single quotes

    async def say_async(self, words):
        """Asynchronously say words."""
        sanitized_words = self.sanitize_text(words)  # Sanitize the words first
        await asyncio.to_thread(self.say, sanitized_words)

    def say(self, words):
        """Speak the given words using the selected TTS engine."""
        sanitized_words = self.sanitize_text(words)  # Sanitize the words before passing
        self.flite(sanitized_words)  # Call flite method directly

    def flite(self, words):
        """Say words using Flite with dynamic parameters."""
        self._debug(f'flite: [{words}]')
        if not self._check_executable(self.FLITE):
            self._debug('flite is busy. Pass')

        # Sanitize the input words to prevent issues with special characters
        sanitized_words = self.sanitize_text(words)

        # Pass in the dynamic parameters for voice, duration, and pitch
        cmd = (f'flite "{sanitized_words}" '
               f'--setf duration_stretch={self.duration_stretch} '
               f'--setf int_f0_target_mean={self.pitch} '
               f'-voice {self.voice_path} '
               f'-o /tmp/tts.wav && aplay /tmp/tts.wav 2>/dev/null &')

        status, result = run_command(cmd)
        if len(result) != 0:
            raise Exception(f'tts-flite:\n\t{result}')
        self._debug(f'command: {cmd}')

    def set_volume(self, volume_percent):
        """Set the system volume via amixer."""
        os.system(f"amixer set Master {volume_percent}%")

    def _debug(self, message):
        """Print debug messages. Modify as necessary for your logging."""
        print(message)
