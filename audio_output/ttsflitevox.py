#!/usr/bin/env python3
from utils.basic import _Basic_class
from utils.utils import is_installed, run_command
from distutils.spawn import find_executable
import os
import re

class TTSFLITE(_Basic_class):
    """Text to speech class using Flite"""
    _class_name = 'TTS'
    FLITE = 'flite'  # Flite TTS engine

    def __init__(self, engine=FLITE, voice_path=None, duration_stretch=1.0, pitch=120, *args, **kwargs):
        """
        Initialize TTS class with Flite-specific parameters.

        :param engine: TTS engine, default is Flite.
        :param voice_path: Path to the Flite voice file.
        :param duration_stretch: Stretch factor for cadence.
        :param pitch: Target pitch (fundamental frequency).
        """
        super().__init__()
        self.engine = engine
        self.voice_path = voice_path
        self.duration_stretch = duration_stretch
        self.pitch = pitch

        if engine == self.FLITE and not is_installed(self.FLITE):
            raise Exception("TTS engine: Flite is not installed.")

    def _check_executable(self, executable):
        """Check if a given executable is available on the system."""
        return find_executable(executable) is not None

    def sanitize_text(self, words):
        """Sanitize text to avoid shell-related issues."""
        sanitized = re.sub(r"[^\w\s']", '', words)  # Allow alphanumeric, spaces, and single quotes
        return sanitized.strip()

    def say(self, words):
        """Speak the words using Flite."""
        sanitized_words = self.sanitize_text(words)
        self.flite(sanitized_words)

    def flite(self, words):
        """Generate speech using Flite."""
        if not self._check_executable(self.FLITE):
            raise RuntimeError("Flite engine is unavailable.")
        
        if not self.voice_path:
            raise ValueError("Voice path is not set for Flite.")

        cmd = (f'flite -voice {self.voice_path} -setf duration_stretch={self.duration_stretch} '
               f'-setf int_f0_target_mean={self.pitch} '
               f'"{words}" -o /tmp/tts.wav && aplay /tmp/tts.wav 2>/dev/null &')
        status, result = run_command(cmd)
        if status != 0:
            raise RuntimeError(f"Flite command failed: {result}")

    def set_flite_params(self, duration_stretch=None, pitch=None):
        """Update Flite parameters."""
        if duration_stretch is not None:
            self.duration_stretch = duration_stretch
        if pitch is not None:
            self.pitch = pitch
