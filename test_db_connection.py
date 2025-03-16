import asyncio
from helpers.system_prompts import get_system_prompt

async def test():
    recognized_speaker = "dad"  # Change this to test different voices
    user_emotion = "neutral"  

    prompt = await get_system_prompt(recognized_speaker, user_emotion)
    print(f"Fetched Prompt:\n{prompt}")

asyncio.run(test())
