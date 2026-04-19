import aiohttp
import asyncio
import json

GATEWAY_URL = "http://192.168.0.123:9000/api/inference"

async def main():
    user_input = """
You are ROBOT1.0. You are in diagnostics mode.
Update all fields for components, services, systems, and sensor data you have access to.
No field should left blank.
If an element is unresponsive, indicate that in the relevant field.  
All JSON elements must be updated to currently known state and include valid values.
    """
    payload = {
        "perception": {
            "user_text": user_input,
            "speaker": "Bob",
            "user_emotion": "happy"
        },
        "world_state": {},
        "memory": {},
        "behavior_state": {},
        "last_intent": "conversation"
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
