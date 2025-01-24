import subprocess
import json
import sounddevice as sd
from vosk import Model, KaldiRecognizer
import asyncio
import numpy as np


async def speak_with_flite(words):
    """Speak the given words using Flite asynchronously."""
    voice_path = "/home/msutt/hal/flitevox/cmu_us_rms.flitevox"
    pitch = 50  # default 100 - higher/deeper voice correlates to higher/lower number
    speed = 0.88  # default 1.0 - higher values stretch the waveform (longer), lower compresses
    try:
        command = [
            "flite",
            "-voice", voice_path,
            "--setf", f"int_f0_target_mean={pitch}",
            "--setf", f"duration_stretch={speed}",
            "-t", words,
        ]
        await asyncio.to_thread(subprocess.run, command, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")
    except FileNotFoundError:
        print("Flite command not found. Ensure it is installed and in the PATH.")


def recognize_speech_vosk(return_audio=False):
    """Recognize speech using Vosk and return the transcribed text."""
    model_path = "/home/msutt/hal/vosk_models/vosk-model-small-en-us-0.15"
    model = Model(model_path)
    recognizer = KaldiRecognizer(model, 44100)

    # Hardcoded device index
    device_index = 1  # Use the correct index for your microphone
    audio_buffer = []   
    stream = None
    try:
        # Initialize the audio stream with the hardcoded index
        stream = sd.RawInputStream(samplerate=44100, blocksize=8000, dtype='int16',
                                   channels=1, device=device_index)
        stream.start()  # Explicitly start the stream
        print("Listening...")
        while True:
            data, _ = stream.read(8000)  # Read raw audio data
            audio_buffer.append(data)  # Save audio for voiceprint
            data = bytes(data)  # Convert to raw byte array

            if recognizer.AcceptWaveform(data):
                result = recognizer.Result()
                text = json.loads(result)["text"]
                if text:
                    if return_audio:
                        return text, np.frombuffer(b"".join(audio_buffer), dtype=np.int16)
                    return text
    except Exception as e:
        print(f"Error during audio processing: {e}")
        raise
    finally:
        # Ensure the microphone is released
        if stream:
            stream.stop()
            stream.close()
            print("Audio stream cleaned up successfully.")


