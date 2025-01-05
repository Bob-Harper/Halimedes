import os
import sys

# Manually add the virtual environment site-packages to sys.path
venv_path = "/home/msutt/hal/venv/lib/python3.11/site-packages"
sys.path.insert(0, venv_path)

import time
import speech_recognition as sr
from robot_hat import TTS

# Initialize recognizer
recognizer = sr.Recognizer()
# Initialize TTS
tts = TTS(engine='espeak')
tts.espeak_params(amp=50, speed=130, gap=2, pitch=40)

# Define the audio capture function
def capture_and_transcribe(mic_index):
    tts.lang("en-US")
    try:
        with sr.Microphone(device_index=mic_index) as source:
            print("Adjusting for ambient noise... Please wait.")
            recognizer.adjust_for_ambient_noise(source)
            print("Ready to detect voice...")

            listening = False
            start_time = None
            timeout_duration = 4  # Adjust as needed

            while True:
                # Adjust energy threshold (optional)
                recognizer.energy_threshold = 300  # Adjust as needed, default is 4000 for Sphinx

                audio_data = recognizer.listen(source, timeout=timeout_duration)

                if audio_data:
                    if not listening:
                        print("Detected a voice, listening closely...")
                        listening = True
                        start_time = time.time()

                    # Attempt to recognize speech
                    try:
                        text = recognizer.recognize_sphinx(audio_data)
                        print(f"Transcribed text: {text}")

                        # Here you can process the transcribed text further
                        # For now, we print a message indicating transcription success
                        print("Transcription complete.")

                        # Simulate further processing (e.g., sending to LLM and TTS)
                        print("Processing with LLM and TTS...")
                        # Use TTS to speak the response
                        tts.say(text)

                        # Reset flags for next round
                        listening = False
                        start_time = None

                    except sr.UnknownValueError:
                        print("Sphinx could not understand the audio")
                    except sr.RequestError as e:
                        print(f"Could not request results from Sphinx service; {e}")

                else:
                    if listening and time.time() - start_time > 2:  # Adjust silence detection time as needed
                        print("Talking stopped, let me process now...")
                        listening = False
                        start_time = None
                    elif not listening:
                        print("No audio input detected. Waiting...")

    except Exception as e:
        print(f"Error capturing audio: {e}")

if __name__ == "__main__":
    mic_index = 1  # Change this to the correct device index from the previous script
    capture_and_transcribe(mic_index)

