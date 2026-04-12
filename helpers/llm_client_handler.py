import requests
import asyncio
from typing import Dict, Any


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

    async def send_message_async(self, payload: dict, retries: int = 2) -> Dict[str, Any]:
        """
        Send a JSON payload to the unified server and return JSON.
        Includes:
        - timeout
        - retries
        - safe fallback
        """
        url = f"{self.server_host}/api/unified"

        for attempt in range(retries + 1):
            try:
                response = await asyncio.to_thread(
                    requests.post,
                    url,
                    json=payload,
                    timeout=10
                )

                response.raise_for_status()

                # Validate JSON
                try:
                    data = response.json()
                    if isinstance(data, dict):
                        return data
                    else:
                        raise ValueError("Server returned non-dict JSON")

                except Exception as json_err:
                    print(f"[UnifiedServer] Invalid JSON: {json_err}")

            except Exception as e:
                print(f"[UnifiedServer] Attempt {attempt+1}/{retries+1} failed: {e}")

            # Retry delay (simple linear backoff)
            await asyncio.sleep(0.2 * (attempt + 1))

        # FINAL FALLBACK — never crash the robot
        return {
            "intent": "observe",
            "speech": {"utterances": []},
            "nonverbal": {},
            "memory": {},
            "world_state": {}
        }