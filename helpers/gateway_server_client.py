import aiohttp
import base64
import subprocess
import tempfile
import time
import uuid
import json


class GatewayClient:
    def __init__(self, server_host: str):
        self.server_host = server_host.rstrip("/")

    # -------------------------
    # 1. Transcription
    # -------------------------
    async def transcribe_audio(self, audio_bytes: bytes):

        # 1. Write raw PCM to a temp file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".raw") as tmp_in:
            in_path = tmp_in.name
            tmp_in.write(audio_bytes)

        # 2. Convert raw PCM → 16k WAV
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_out:
            out_path = tmp_out.name

        subprocess.run([
            "ffmpeg",
            "-y",
            "-f", "s16le",                 # raw PCM
            "-ar", "44100",                # original sample rate
            "-ac", "1",                    # mono
            "-i", in_path,                 # input raw file

            # --- OUTPUT FORMAT ---
            "-ac", "1",
            "-ar", "16000",                # final sample rate for Vosk
            "-sample_fmt", "s16",
            out_path
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        # 3. Load converted WAV
        wav_bytes = open(out_path, "rb").read()

        # 4. Base64 encode
        audio_b64 = base64.b64encode(wav_bytes).decode("ascii")
        payload = {"audio_b64": audio_b64}
        url = f"{self.server_host}/api/transcribe"

        req_id = str(uuid.uuid4())
        t0 = time.monotonic()

        print(f"[GatewayClient] [{req_id}] POST {url}")
        print(f"[GatewayClient] [{req_id}] Payload size: raw={len(wav_bytes)} bytes, b64={len(audio_b64)} chars")

        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(
                    url,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=60)
                ) as resp:
                    t1 = time.monotonic()
                    text = await resp.text()
                    print(f"[GatewayClient] [{req_id}] Status={resp.status} RTT={(t1 - t0)*1000:.2f} ms")
                    print(f"[GatewayClient] [{req_id}] Response raw (first 500): {text[:500]}")
                    try:
                        return json.loads(text)
                    except json.JSONDecodeError as e:
                        print(f"[GatewayClient] [{req_id}] JSON decode error: {repr(e)}")
                        return {"error": "json_decode_error", "detail": text[:500], "text": ""}

            except Exception as e:
                t1 = time.monotonic()
                err_type = type(e).__name__
                print(f"[GatewayClient] [{req_id}] EXCEPTION after {(t1 - t0)*1000:.2f} ms: {err_type}: {repr(e)}")
                return {"error": err_type, "detail": repr(e), "text": ""}
            
    # -------------------------
    # 2. Unified cognition
    # -------------------------
    async def send_perception(self, payload: dict):
        url = f"{self.server_host}/api/inference"

        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload) as resp:
                return await resp.json()    
            
    # -------------------------
    # 4. Face Recognition (future)
    # -------------------------
    async def recognize_face(self, image_bytes: bytes):
        # placeholder for future endpoint
        pass

    # -------------------------
    # 6. Memory Operations (future)
    # -------------------------
    async def store_memory(self, text: str, tags: list):
        pass

    async def query_memory(self, query: str):
        pass
    