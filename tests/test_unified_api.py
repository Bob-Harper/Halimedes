import aiohttp
import asyncio
import json
from pathlib import Path
prompt_file = Path("/home/msutt/hal/mind/system_prompt.txt")

GATEWAY_URL = "http://192.168.0.123:9000/api/unified"

async def main():
    # This simulates what Hal would send after transcription
    if prompt_file.exists():
        with open(prompt_file, "r", encoding="utf-8") as f:
            system_prompt = f.read()
    else:    
        system_prompt = "[ERROR: System prompt file not found]"
    # Keep the /nothink during testing until the reasoining flag is fully implemented        
    user_input = "/nothink You are ROBOT1.0.  You are in diagnostics mode.  Please test all systems and sensors you detect as connected, and present a status report. List each detected system and sensor by name and function. Include any systems you are aware of that apper to be offline or unable to access."

    payload = {
        "perception": {
            "system_prompt": system_prompt,
            "user_text": user_input,
            "world_state": "",
            "behavior_state": "",
            "perception_summary": "",
            "last_intent": "conversation",
            "speaker": "Bob",
            "emotion": "happy",
            "reasoning_required": "False",
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