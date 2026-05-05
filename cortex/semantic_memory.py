# Hard data, objectively interpretable data, facts, information. Can be used for reasoning, logic, etc.
import aiohttp
import logging

logger = logging.getLogger(__name__)

class SemanticMemory:
    def __init__(self, gateway_url: str):
        self.gateway_url = gateway_url.rstrip("/")

    async def write(self, key: str, value: str):
        url = f"{self.gateway_url}/api/memory/semantic/write"
        payload = {"key": key, "value": value}

        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload) as resp:
                if resp.status != 200:
                    logger.error(f"[SemanticMemory] Write failed: {resp.status}")
                    return None
                return await resp.json()

    async def read(self, key: str):
        url = f"{self.gateway_url}/api/memory/semantic/read"
        payload = {"key": key}

        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload) as resp:
                if resp.status != 200:
                    logger.error(f"[SemanticMemory] Read failed: {resp.status}")
                    return None
                return await resp.json()
