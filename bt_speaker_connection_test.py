import asyncio
from helpers.voice_utils import speak_with_flite

async def test_speech():
    await speak_with_flite("This is a test of the Bluetooth speaker output.")

asyncio.run(test_speech())
