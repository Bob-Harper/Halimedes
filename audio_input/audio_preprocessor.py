import tempfile
import subprocess
import numpy as np


class AudioPreprocessor:
    """
    Converts raw PCM (44.1k mono int16) into 16k mono WAV bytes
    using the exact ffmpeg chain that already works perfectly.
    """

    def __init__(self):
        pass

    def pcm_to_16k_wav(self, pcm_audio: np.ndarray) -> bytes:
        """
        Accepts mono int16 PCM at 44.1k (utterance_44k)
        Returns 16k WAV bytes.
        """

        # Ensure 1D mono
        if pcm_audio.ndim > 1:
            pcm_audio = pcm_audio.flatten()

        # 1. Write raw PCM to temp file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".raw") as tmp_in:
            in_path = tmp_in.name
            tmp_in.write(pcm_audio.tobytes())

        # 2. Prepare output WAV path
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_out:
            out_path = tmp_out.name

        # 3. Run ffmpeg chain 
        subprocess.run([
            "ffmpeg",
            "-y",
            "-f", "s16le",          # raw PCM
            "-ar", "44100",         # original sample rate
            "-ac", "1",             # mono
            "-i", in_path,          # input raw file

            # OUTPUT FORMAT
            "-ac", "1",
            "-ar", "16000",         # final sample rate for Vosk
            "-sample_fmt", "s16",
            out_path
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        # 4. Load converted WAV
        wav_bytes = open(out_path, "rb").read()

        return wav_bytes
