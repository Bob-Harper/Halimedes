import sounddevice as sd
import numpy as np
import asyncio
import webrtcvad
import resampy
import queue
import collections
import time


class AudioInputManager:
    """
    AUDIO CAPTURE + RESAMPLE + VAD
    ------------------------------
    - Records from mic at 44.1 kHz (hardware requirement)
    - Resamples to 48 kHz for WebRTC VAD
    - Buffers only speech frames
    - Returns final utterance
    """

    def __init__(
        self,
        picrawler_instance: object,
        input_device_index: int = 1,
        vad_level: int = 2,
        frame_ms: int = 30,
        silence_after_speech: float = 2,
        max_utterance_length: float = 20.0
    ):
        self.picrawler_instance = picrawler_instance

        # Hardware rate (mic only supports 44100)
        self.hw_sample_rate = 44100

        # VAD rate (WebRTC supports 48k)
        self.vad_sample_rate = 48000

        self.vad = webrtcvad.Vad(vad_level)
        self.frame_ms = int(frame_ms)
        self.silence_after_speech = float(silence_after_speech)
        self.max_utterance_length = float(max_utterance_length)

        # Frame sizes
        self.hw_frame_samples = int(self.hw_sample_rate * self.frame_ms / 1000)
        self.vad_frame_samples = int(self.vad_sample_rate * self.frame_ms / 1000)

        sd.default.device = (input_device_index, None)  # type: ignore[arg-type]

    async def capture_audio(self):
        """Returns a full utterance as int16 numpy array at 16 kHz."""
        return await asyncio.to_thread(self._record_with_vad)

    def _record_with_vad(self):

        q = queue.Queue()

        def callback(indata):
            q.put(indata.copy())

        # Match your working VAD config
        frame_duration_ms = 30
        padding_duration_ms = 1000
        num_padding_frames = int(padding_duration_ms / frame_duration_ms)

        ring_buffer = collections.deque(maxlen=num_padding_frames)
        triggered = False

        voiced_frames_44k = []
        start_time = None

        with sd.InputStream(
            samplerate=self.hw_sample_rate,
            channels=1,
            dtype='int16',
            blocksize=self.hw_frame_samples,
            callback=callback
        ):
            while True:
                # 1. Get 30ms at 44.1k from continuous stream
                frame_44k = q.get()  # shape (hw_frame_samples, 1), int16

                # 2. Resample to 48k for VAD
                frame_48k = resampy.resample(
                    frame_44k.flatten().astype(np.float32),
                    self.hw_sample_rate,
                    self.vad_sample_rate
                ).astype(np.int16)

                if len(frame_48k) < self.vad_frame_samples:
                    continue
                frame_48k = frame_48k[:self.vad_frame_samples]

                frame_bytes = frame_48k.tobytes()
                is_speech = self.vad.is_speech(frame_bytes, self.vad_sample_rate)

                if not triggered:
                    # NOT TRIGGERED: fill ring buffer
                    ring_buffer.append((frame_44k, is_speech))
                    num_voiced = sum(1 for f, speech in ring_buffer if speech)

                    # Enter TRIGGERED when >90% voiced
                    if num_voiced > 0.9 * ring_buffer.maxlen: # type: ignore
                        triggered = True
                        start_time = time.time()

                        # Pre-roll: dump ring buffer into voiced frames
                        for f, s in ring_buffer:
                            voiced_frames_44k.append(f)
                        ring_buffer.clear()

                else:
                    # TRIGGERED: collect frames (KEEP EVERYTHING)
                    voiced_frames_44k.append(frame_44k)
                    ring_buffer.append((frame_44k, is_speech))

                    num_unvoiced = sum(1 for f, speech in ring_buffer if not speech)

                    # If >90% unvoiced → end utterance
                    if num_unvoiced > 0.9 * ring_buffer.maxlen: # type: ignore
                        break

                    # Safety cap
                    if (time.time() - start_time) > self.max_utterance_length: # type: ignore
                        break

        if not voiced_frames_44k:
            return None

        utterance_44k = np.concatenate(voiced_frames_44k, axis=0).astype(np.int16)

        return utterance_44k

    def analyze_voice_input(self, raw_bytes, recognized_speaker):    
        # Placeholder for future voice analysis (Should Hal Respond To This Voice)
        # For now, just print the raw byte length and speaker
        print(f"[Voice Analysis] {len(raw_bytes)} bytes from speaker '{recognized_speaker}'")
        return True