import requests
import asyncio
import json


class LLMClientHandler:
    """
    Unified Server Client
    - Sends dict payloads
    - Receives dict responses
    - No chat history
    - No system prompts
    - No personalities
    """

    def __init__(self, server_host: str):
        self.server_host = server_host.rstrip("/")

    async def send_message_async(self, payload: dict) -> dict:
        """
        Send a JSON payload to the unified server and return JSON.
        """
        try:
            response = await asyncio.to_thread(
                requests.post,
                f"{self.server_host}/api/unified",
                json=payload,
                timeout=10
            )

            response.raise_for_status()
            return response.json()

        except Exception as e:
            print(f"[UnifiedServer] Error: {e}")
            return {
                "intent": "observe",
                "speech": {"utterances": []},
                "nonverbal": {},
                "memory": {},
                "world_state": {}
            }