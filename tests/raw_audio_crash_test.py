import numpy as np
from audio_input.voice_recognition_manager import VoiceRecognitionManager

v = VoiceRecognitionManager()

# Fake 1 second of 44.1kHz int16 audio
fake = (np.random.randn(44100) * 3000).astype(np.int16)

print(v.recognize_speaker(fake))
