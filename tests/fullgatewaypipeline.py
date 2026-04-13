import aiohttp
import asyncio
import base64
import json
import os

TRANSCRIBE_URL = "http://192.168.0.123:9000/api/transcribe"
UNIFIED_URL    = "http://192.168.0.123:9000/api/unified"

AUDIO_FILE = "/home/msutt/Music/Recording.m4a"   # change if needed

async def main():
    # -----------------------------
    # 1. Load WAV
    # -----------------------------
    if not os.path.exists(AUDIO_FILE):
        print(f"Audio file not found: {AUDIO_FILE}")
        return

    print(f"[Test] Loading audio: {AUDIO_FILE}")
    audio_bytes = open(AUDIO_FILE, "rb").read()
    print(f"[Test] Loaded {len(audio_bytes)} bytes")

    # -----------------------------
    # 2. Send to /api/transcribe
    # -----------------------------
    audio_b64 = base64.b64encode(audio_bytes).decode("utf-8")
    transcribe_payload = {"audio_b64": audio_b64}

    async with aiohttp.ClientSession() as session:
        print(f"[Test] Sending to {TRANSCRIBE_URL}")
        async with session.post(TRANSCRIBE_URL, json=transcribe_payload) as resp:
            transcribe_raw = await resp.text()
            print(f"[Test] Transcribe status: {resp.status}")
            print(f"[Test] Transcribe raw: {transcribe_raw}")

            try:
                transcribe_json = json.loads(transcribe_raw)
            except:
                print("[Test] Failed to parse transcription JSON")
                return

    transcribed_text = transcribe_json.get("text", "")
    print(f"[Test] Transcribed text: {transcribed_text}")

    # -----------------------------
    # 3. Build unified payload
    # -----------------------------
    unified_payload = {
        "perception": {
            "user_text": "/nothink " + transcribed_text,
            "user_emotion": "neutral",
            "speaker": "Bob"
        }
    }

    # -----------------------------
    # 4. Send to /api/unified
    # -----------------------------
    async with aiohttp.ClientSession() as session:
        print(f"[Test] Sending unified snapshot to {UNIFIED_URL}")
        async with session.post(UNIFIED_URL, json=unified_payload) as resp:
            unified_raw = await resp.text()
            print(f"[Test] Unified status: {resp.status}")
            print(f"[Test] Unified raw: {unified_raw}")

            try:
                unified_json = json.loads(unified_raw)
                print("[Test] Unified parsed:")
                print(json.dumps(unified_json, indent=2))
            except:
                print("[Test] Failed to parse unified JSON")

if __name__ == "__main__":
    asyncio.run(main())