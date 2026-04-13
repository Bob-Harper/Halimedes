import sounddevice as sd
import numpy as np
import asyncio


class AudioInputManager:
    """
    PURE AUDIO CAPTURE LAYER
    ------------------------
    - Records microphone audio until silence is detected.
    - Returns raw audio as a 1D int16 numpy array.
    - Does NOT perform transcription.
    - Does NOT talk to Vosk.
    - Does NOT talk to unified server.
    - Does NOT handle LED or sound indicators.
    """

    def __init__(
        self,
        picrawler_instance,
        sample_rate=44100,
        input_device_index=1,
        silence_threshold=700,
        silence_duration=2.0,
        block_duration=1.0,
    ):
        self.picrawler_instance = picrawler_instance
        self.sample_rate = sample_rate
        self.silence_threshold = silence_threshold
        self.silence_duration = silence_duration
        self.block_duration = block_duration

        # Force sounddevice to use the correct microphone.
        # Pylance/InsertCheckerHere doesn't recognize this as valid, but it is hardware accurate and will run.
        sd.default.device = (input_device_index, None) # type: ignore


    # ------------------------------------------------------------------
    # PUBLIC API
    # ------------------------------------------------------------------
    async def capture_audio(self):
        """
        Record audio until silence is detected.
        Returns:
            raw_audio (np.ndarray[int16]) — 1D array of audio samples
        """
        audio_array = await asyncio.to_thread(
            self._record_until_silence
        )
        return np.ravel(audio_array)

    # ------------------------------------------------------------------
    # INTERNAL AUDIO CAPTURE LOGIC
    # ------------------------------------------------------------------
    def _record_until_silence(self):
        """
        Blocking call — runs inside a thread via asyncio.to_thread().
        """
        blocks = []
        silence_time = 0.0
        block_samples = int(self.sample_rate * self.block_duration)
        has_spoken = False

        while True:
            audio_block = sd.rec(
                block_samples,
                samplerate=self.sample_rate,
                channels=1,
                dtype='int16'
            )
            sd.wait()

            blocks.append(audio_block)
            amplitude = np.abs(audio_block).mean()

            if amplitude < self.silence_threshold:
                if has_spoken:
                    silence_time += self.block_duration
            else:
                has_spoken = True
                silence_time = 0.0

            if has_spoken and silence_time >= self.silence_duration:
                break

        return np.concatenate(blocks, axis=0)