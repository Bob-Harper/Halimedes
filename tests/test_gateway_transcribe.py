import aiohttp
import asyncio
import base64
import json
import os
import subprocess
import tempfile

GATEWAY_URL = "http://192.168.0.123:9000/api/transcribe"
# AUDIO_FILE = "/home/msutt/Music/ljspeech-vits.wav"   # change if needed /home/msutt/Music/Recording.m4a
AUDIO_FILE = "/home/msutt/Music/Recording.m4a"
async def main():
    if not os.path.exists(AUDIO_FILE):
        print(f"Audio file not found: {AUDIO_FILE}")
        return

    print(f"[Test] Loading audio: {AUDIO_FILE}")
    # Convert to 16k WAV using ffmpeg
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_out:
        out_path = tmp_out.name

    subprocess.run([
        "ffmpeg",
        "-y",
        "-i", AUDIO_FILE,
        "-ac", "1",
        "-ar", "16000",
        "-sample_fmt", "s16",
        out_path
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    # Load the converted audio
    audio_bytes = open(out_path, "rb").read()

    print(f"[Test] Loaded {len(audio_bytes)} bytes")

    # Hal sends base64 JSON
    audio_b64 = base64.b64encode(audio_bytes).decode("utf-8")
    payload = {"audio_b64": audio_b64}

    async with aiohttp.ClientSession() as session:
        print(f"[Test] Sending to {GATEWAY_URL}")
        async with session.post(GATEWAY_URL, json=payload) as resp:
            text = await resp.text()
            print(f"[Test] Response status: {resp.status}")
            print(f"[Test] Raw response: {text}")

            try:
                data = json.loads(text)
                print(f"[Test] Parsed JSON: {data}")
            except:
                print("[Test] Failed to parse JSON")

if __name__ == "__main__":
    asyncio.run(main())