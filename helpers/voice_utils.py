import subprocess
import json
import re
import sounddevice as sd
from vosk import Model, KaldiRecognizer
import asyncio
import numpy as np
import websockets
from helpers.emotions import get_voice_modifiers
from helpers.emotions import EmotionHandler

"""
pitch = 50  # flite default 100 - higher/deeper voice correlates to higher/lower number
speed = 0.88  # flite default 1.0 - higher values stretch the waveform (longer), lower compresses

"""
# Hal's voicefile, modified with the following values
voice_path = "/home/msutt/hal/flitevox/cmu_us_rms.flitevox"
# Baseline values for Hal's signature voice
baseline_pitch = 50
baseline_speed = 0.88

emotion_handler = EmotionHandler()


async def speak_with_flite(words, emotion="neutral"):
    """
    Speak using a single pitch and speed for the entire speech output.

    """
    # Get relative adjustment factors for pitch and speed
    emotion_settings = get_voice_modifiers(emotion)
    pitch_factor = emotion_settings["pitch_factor"]
    speed_factor = emotion_settings["speed_factor"]

    # Calculate modified pitch and speed
    pitch = int(baseline_pitch * pitch_factor)
    speed = round(baseline_speed * speed_factor, 2)

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


async def speak_with_dynamic_flite(full_text):
    """Speak with adaptive pitch and speed modulation dynamically for each sentence fragment."""
    try:
        # Step 1: Split the text into logical fragments (sentences/clauses)
        fragments = re.split(r'[.,;!?]\s*', full_text)
        fragments = [frag.strip() for frag in fragments if frag.strip()]  # Clean empty strings

        # Step 2: Process each fragment individually
        for fragment in fragments:
            # Determine the emotion for the fragment
            fragment_emotion = emotion_handler.analyze_text_emotion(fragment)
            emotion_settings = get_voice_modifiers(fragment_emotion)
            pitch = int(baseline_pitch * emotion_settings["pitch_factor"])
            speed = round(baseline_speed * emotion_settings["speed_factor"], 2)

            print(f"Speaking fragment '{fragment}' with emotion '{fragment_emotion}': pitch={pitch}, speed={speed}")

            # Speak the fragment with calculated pitch and speed
            command = [
                "flite",
                "-voice", voice_path,
                "--setf", f"int_f0_target_mean={pitch}",
                "--setf", f"duration_stretch={speed}",
                "-t", fragment,
            ]
            await asyncio.to_thread(subprocess.run, command, check=True)

    except Exception as e:
        print(f"Error in adaptive speech, falling back to neutral: {e}")
        # Fallback to the default flite with no modulation
        await speak_with_flite(full_text)


async def recognize_speech_vosk(server_url="ws://192.168.0.123:2700", return_audio=False):
    """
    Records audio until silence is detected and processes it using either:
    - The Vosk server (default path)
    - The small Vosk model locally (fallback path if the server is truly unavailable).
    Returns the transcript and optionally the raw audio.
    """
    audio_array = await asyncio.to_thread(record_until_silence)
    # audio_array = denoise_audio(audio_array)
    audio_array = np.ravel(audio_array)  # Flatten audio to 1D
    audio_bytes = audio_array.tobytes()

    try:
        # Try processing via the Vosk server
        transcript = await process_audio_with_transcriber(
            transcribe_via_server, audio_bytes, server_url
        )
        print(f"Transcript: {transcript}")
    except websockets.exceptions.ConnectionClosedOK:
        print("Server completed successfully, no fallback needed.")
        # If the server closed normally (1000 OK), just return the transcript
        return transcript, audio_array if return_audio else transcript

    except Exception as e:
        print(f"Unexpected server error, switching to fallback: {e}")
        # If there was an actual error, process locally
        transcript = await process_audio_with_transcriber(
            transcribe_via_fallback, audio_bytes
        )
        
    # Remove "the" at the start of the transcript if present
    if transcript.lower().startswith("the "):
        transcript = transcript[4:]  # Trim the first occurrence of "the" + space
    
    if return_audio:
        return transcript, audio_array
    return transcript


async def process_audio_with_transcriber(transcriber, audio_bytes, *transcriber_args):
    """
    Shared logic for chunking audio and collecting the transcript.
    Handles server closure properly.
    """
    chunk_size = 4000
    final_text_parts = []

    try:
        async for chunk_result in transcriber(audio_bytes, chunk_size, *transcriber_args):
            if "text" in chunk_result and chunk_result["text"].strip():
                final_text_parts.append(chunk_result["text"].strip())
    except websockets.exceptions.ConnectionClosedOK:
        # Handle graceful connection closure without crashing
        pass
    except Exception as e:
        print(f"Unexpected error in transcriber: {e}")

    # Final combined transcript
    final_text = " ".join(final_text_parts).strip()
    return final_text or "No transcript available"


async def transcribe_via_server(audio_bytes, chunk_size, server_url):
    """
    Sends audio to the Vosk server chunk-by-chunk.
    """
    async with websockets.connect(server_url) as ws:

        for i in range(0, len(audio_bytes), chunk_size):
            await ws.send(audio_bytes[i:i + chunk_size])
        await ws.send('{"eof" : 1}')

        while True:
            try:
                message = await asyncio.wait_for(ws.recv(), timeout=5)
                print(f"message: {message}")

                yield json.loads(message)
            except asyncio.TimeoutError:
                break


async def transcribe_via_fallback(audio_bytes, chunk_size):
    """
    Transcribes audio locally using the small Vosk model.
    """
    model_path = "/home/msutt/hal/vosk_models/vosk-model-small-en-us-0.15"
    model = Model(model_path)
    recognizer = KaldiRecognizer(model)

    for i in range(0, len(audio_bytes), chunk_size):
        chunk = audio_bytes[i:i + chunk_size]
        if recognizer.AcceptWaveform(chunk):
            yield json.loads(recognizer.Result())


def record_until_silence(sample_rate=44100, block_duration=1.0, silence_threshold=600, silence_duration=2.0):
    """
    Records audio until silence is detected for at least `silence_duration` seconds.
    """
    blocks = []
    silence_time = 0.0
    block_samples = int(sample_rate * block_duration)
    has_spoken = False

    print("Recording started. Please speak...")

    while True:
        audio_block = sd.rec(block_samples, samplerate=sample_rate, channels=1, dtype='int16')
        sd.wait()
        blocks.append(audio_block)
        amplitude = np.abs(audio_block).mean()

        if amplitude < silence_threshold:
            if has_spoken:
                silence_time += block_duration
        else:
            has_spoken = True
            silence_time = 0.0  # Reset silence timer on sound

        if has_spoken and silence_time >= silence_duration:
            break

    return np.concatenate(blocks, axis=0)
