from helpers.voice_utils import recognize_speech_vosk, speak_with_flite
from helpers.llm_utils import LLMClient
from helpers.emotions import EmotionHandler, EmotionSoundManager
import asyncio


llm_client = LLMClient(server_host='http://192.168.0.123:11434')  #101 = Stygia, 123 = Studio
emotion_handler = EmotionHandler()
emotion_sound_manager = EmotionSoundManager()

async def main():
    await speak_with_flite("I'm ready to chat! Let's have a conversation.")

    while True:
        print("Listening for your input...")
        spoken_text = await recognize_speech_vosk()

        if not spoken_text:
            print("No input detected, waiting...")
            continue

        print(f"User said: {spoken_text}")

        # Detect and play a sound based on user's emotion
        user_emotion = emotion_handler.analyze_text_emotion(spoken_text)
        print(f"Detected user emotion: {user_emotion}")
        emotion_sound_manager.play_sound(user_emotion)

        # Generate a response with user emotion context
        system_prompt = f"You are Halimeedees, a test robot. User emotion detected: {user_emotion}. Keep your response to 50 words or less.  efficient and informative.."
        response_text = await llm_client.send_message_async(system_prompt, spoken_text)
        print(f"Hal said: {response_text}")

        # Detect Hal's emotion from the response and play the corresponding sound
        hal_emotion = emotion_handler.analyze_text_emotion(response_text)
        print(f"Detected Hal's emotion: {hal_emotion}")
        emotion_sound_manager.play_sound(hal_emotion)

        # Speak the response
        await speak_with_flite(response_text)

if __name__ == "__main__":
    asyncio.run(main())
