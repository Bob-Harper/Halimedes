import aiohttp
import asyncio
import json

GATEWAY_URL = "http://192.168.0.123:9000/api/unified"

async def main():
    # This simulates what Hal would send after transcription
    payload = {
        "perception": {
            "user_text": "/nothink Good morning Hal, how are you feeling today?",
            "user_emotion": "neutral",
            "speaker": "Bob"
        }
    }

    print("[Test] Sending unified perception snapshot:")
    print(json.dumps(payload, indent=2))

    async with aiohttp.ClientSession() as session:
        async with session.post(GATEWAY_URL, json=payload) as resp:
            text = await resp.text()
            print(f"[Test] Response status: {resp.status}")
            print(f"[Test] Raw response: {text}")

            try:
                data = json.loads(text)
                print("[Test] Parsed JSON:")
                print(json.dumps(data, indent=2))
            except:
                print("[Test] Failed to parse JSON")

if __name__ == "__main__":
    asyncio.run(main())