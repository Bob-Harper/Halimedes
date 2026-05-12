import aiohttp
import base64
import time
import uuid
import json
from cortex.embedding import Embedder
from cortex.episodic_memory import EpisodicMemory
from cortex.semantic_memory import SemanticMemory

class GatewayClient:
    def __init__(self, server_host: str):
        self.server_host = server_host.rstrip("/")
        self.embedder = Embedder()
        self.semantic = SemanticMemory(self.server_host)
        self.episodic = EpisodicMemory(self.server_host)
        
    # -------------------------
    # 1. Transcription
    # -------------------------
    async def transcribe_audio(self, wav_bytes: bytes):
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
                    timeout=aiohttp.ClientTimeout(total=600)
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
    async def send_perception(self, payload: dict, endpoint):
        url = f"{self.server_host}{endpoint}"

        async with aiohttp.ClientSession() as session:
            async with session.post(
                url,
                json=payload,
                timeout=aiohttp.ClientTimeout(total=600)
            ) as resp:
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
    async def store_memory(self, text: str, tags: list[str] | None = None):
        """
        High-level memory write used by HAL.
        - Creates embedding
        - Stores episodic memory
        - Optionally stores semantic tags
        """
        # 1. embed text (HAL already has embed() in cognition)
        vector = self.embedder.embed(text)

        # 2. episodic memory write
        result = await self.episodic.store(content=text, vector=vector)

        # 3. optional semantic tags
        if tags:
            for tag in tags:
                await self.semantic.write(tag, text)

        return result

    async def query_memory(self, query: str, top_k: int = 5):
        """
        High-level memory search used by HAL.
        - Embeds query
        - Vector search episodic memory
        - Returns structured results
        """
        qvec = self.embedder.embed(query)

        return await self.episodic.search(qvec, top_k=top_k)