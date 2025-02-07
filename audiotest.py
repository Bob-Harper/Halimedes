import sounddevice as sd
import numpy as np

# Set sampling rate and duration for the test
samplerate = 44100
duration = 10  # 10 seconds of recording

print("Recording for 10 seconds...")
# Change channels=1 to use mono input
audio = sd.rec(int(samplerate * duration), samplerate=samplerate, channels=1, dtype='int16')
sd.wait()

# Check if any audio was captured properly
if np.any(audio):
    print("Audio was successfully recorded.")
else:
    print("No audio was detected.")
