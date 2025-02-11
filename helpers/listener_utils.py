import json
import sounddevice as sd
from vosk import Model, KaldiRecognizer
import asyncio
import numpy as np
import websockets
from helpers.passive_sounds import PassiveSoundsManager
from helpers.general_utilities import GeneralUtilities
from gpiozero import LED


class AudioInput:
    def __init__(self, silence_threshold=700, silence_duration=2.0, sample_rate=44100):
        self.sound_manager = PassiveSoundsManager()
        self.general_utils = GeneralUtilities()
        self.silence_threshold = silence_threshold
        self.silence_duration = silence_duration
        self.sample_rate = sample_rate
        # Initialize the listening LED pin
        self.listening_led = LED(26)

    async def recognize_speech_vosk(self, server_url="ws://192.168.0.123:2700", return_audio=False):
        """
        Records audio until silence is detected and processes it using either:
        - The Vosk server (default path)
        - The small Vosk model locally (fallback path if the server is truly unavailable).
        Returns the transcript and optionally the raw audio.
        """
        # Turn on Indicators for Active Listening.
        await self.sound_manager.play_sound_indicator("/home/msutt/hal/sounds/passive/excited/n-talk3.wav", 10)
        led_task = asyncio.create_task(self._led_blip())

        audio_array = await asyncio.to_thread(self.record_until_silence)
        audio_array = np.ravel(audio_array)  # Flatten audio to 1D
        audio_bytes = audio_array.tobytes()

        # Turn off Indicators for Active Listening.
        led_task.cancel()
        try:
            await led_task  # Ensure it stops cleanly
        except asyncio.CancelledError:
            pass
        await self.sound_manager.play_sound_indicator("/home/msutt/hal/sounds/passive/excited/n-talk1.wav", 10)
        self.listening_led.off()

        try:
            # Try processing via the Vosk server
            transcript = await self.process_audio_with_transcriber(
                self.transcribe_via_server, audio_bytes, server_url
            )
        except websockets.exceptions.ConnectionClosedOK:
            # If the server closed normally (1000 OK), just return the transcript
            return transcript, audio_array if return_audio else transcript

        except Exception as e:
            print(f"Unexpected server error, switching to fallback: {e}")
            # If there was an actual error, process locally
            transcript = await self.process_audio_with_transcriber(
                self.transcribe_via_fallback, audio_bytes
            )
            
        # Remove "the" at the start of the transcript if present
        if transcript.lower().startswith("the "):
            transcript = transcript[4:]  # Trim the first occurrence of "the" + space
        
        if return_audio:
            return transcript, audio_array
        return transcript

    @staticmethod
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

    @staticmethod
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
                    yield json.loads(message)
                except asyncio.TimeoutError:
                    break

    @staticmethod
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

    @staticmethod
    def record_until_silence(sample_rate=44100, block_duration=1.0, silence_threshold=700, silence_duration=2.0):
        """
        Records audio until silence is detected for at least `silence_duration` seconds.
        """
        blocks = []
        silence_time = 0.0
        block_samples = int(sample_rate * block_duration)
        has_spoken = False

        # print("Recording started. Please speak...")

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

        # print("Recording stopped. Stand By...")            
        return np.concatenate(blocks, axis=0)

    async def _led_blip(self):
        """Blinks the LED every 2 seconds while listening."""
        while True:
            self.listening_led.on()
            await asyncio.sleep(0.1)  # LED on for 0.1 seconds
            self.listening_led.off()
            await asyncio.sleep(1.9)  # LED off for 1.9 seconds