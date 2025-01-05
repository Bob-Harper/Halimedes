import sounddevice as sd
import numpy as np

# Specify the microphone index based on your previous findings
mic_index = 1  # USB PnP Sound Device

# Callback function to process the audio input
def callback(indata, frames, time, status):
    if status:
        print(status)  # Print any warnings
    # Here you could process the indata, e.g., for speech recognition

    # For demonstration, just print how many frames were captured
    print(f"Captured {frames} frames.")

try:
    # Open an input stream using the specified microphone index
    with sd.InputStream(device=mic_index, channels=1, samplerate=44100, callback=callback):
        print("Listening... Press Ctrl+C to stop.")
        sd.sleep(100)  # Listen for 10 seconds
except Exception as e:
    print(f"Error: {e}")
