import aiohttp
import base64
import numpy as np

class GatewayClient:
    def __init__(self, server_host: str):
        self.server_host = server_host.rstrip("/")

    # -------------------------
    # 1. Transcription
    # -------------------------
    async def transcribe_audio(self, raw_audio: np.ndarray):
        audio_bytes = raw_audio.tobytes()
        audio_b64 = base64.b64encode(audio_bytes).decode("ascii")

        payload = {"audio_b64": audio_b64}
        url = f"{self.server_host}/api/transcribe"

        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(url, 
                                        json=payload, 
                                        timeout=aiohttp.ClientTimeout(total=5)) as resp:
                    return await resp.json()
            except Exception as e:
                print(f"[GatewayClient] Gateway unreachable: {e}")
                return {"error": "gateway_unreachable", "text": ""}

    # -------------------------
    # 2. Unified cognition
    # -------------------------
    async def send_perception(self, payload: dict):
        url = f"{self.server_host}/api/unified"

        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload) as resp:
                return await resp.json()    
            
    # -------------------------
    # 3. Speaker ID (future)
    # -------------------------
    async def identify_speaker(self, raw_audio: np.ndarray):
        # placeholder for future endpoint
        pass

    # -------------------------
    # 4. Face Recognition (future)
    # -------------------------
    async def recognize_face(self, image_bytes: bytes):
        # placeholder for future endpoint
        pass

    # -------------------------
    # 5. Emotion Analysis (future)
    # -------------------------
    async def analyze_emotion(self, raw_audio: np.ndarray):
        # placeholder for future endpoint
        pass

    # -------------------------
    # 6. Memory Operations (future)
    # -------------------------
    async def store_memory(self, text: str, tags: list):
        pass

    async def query_memory(self, query: str):
        pass