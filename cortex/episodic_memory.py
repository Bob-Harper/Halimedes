# Experiences, conversations, knowledge of users. Subjectivele interpretable data
import aiohttp
import logging
import time

logger = logging.getLogger(__name__)

class EpisodicMemory:
    def __init__(self, gateway_url: str):
        self.gateway_url = gateway_url.rstrip("/")

    async def store(self, content: str, vector: list[float], timestamp: float | None = None):
        if timestamp is None:
            timestamp = time.time()

        url = f"{self.gateway_url}/api/memory/episodic/write"
        payload = {
            "content": content,
            "vector": vector,
            "timestamp": timestamp
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload) as resp:
                if resp.status != 200:
                    logger.error(f"[EpisodicMemory] Store failed: {resp.status}")
                    return None
                return await resp.json()

    async def search(self, vector: list[float], top_k: int = 5):
        url = f"{self.gateway_url}/api/memory/episodic/search"
        payload = {
            "vector": vector,
            "top_k": top_k
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload) as resp:
                if resp.status != 200:
                    logger.error(f"[EpisodicMemory] Search failed: {resp.status}")
                    return None
                return await resp.json()
