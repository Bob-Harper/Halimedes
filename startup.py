import warnings
import asyncio
import os
from helpers.response_utils import Response_Manager
from helpers.listener_utils import AudioInput
from helpers.verbal_commands import CommandManager
from helpers.voice_recognition import VoiceprintManager
from helpers.emotions import EmotionHandler, EmotionSoundManager
from helpers.weather_commands import WeatherCommandManager
from helpers.llm_utils import LLMClient
from helpers.passive_actions import PassiveActionsManager
from helpers.system_prompts import get_system_prompt
from helpers.general_utilities import GeneralUtilities
from dotenv import load_dotenv

# Load environment variables from a .env file
load_dotenv()
llm_server_url = os.getenv("OLLAMALAPTOP")
warnings.simplefilter('ignore')

# Initialize everything at module level (outside the main() function) as needed:
llm_client = LLMClient(server_host=llm_server_url)
voiceprint_manager = VoiceprintManager()
command_manager = CommandManager(llm_client)
response_manager = Response_Manager()
audio_input = AudioInput()
emotion_handler = EmotionHandler()
emotion_sound_manager = EmotionSoundManager()
actions_manager = PassiveActionsManager()
general_utils = GeneralUtilities()
weather_fetch = WeatherCommandManager(llm_client, actions_manager, emotion_sound_manager)


async def main():
    await response_manager.speak_with_flite("Beginning startup procedure and status check. Please stand by, system test underway.")
    await response_manager.speak_with_flite("Servos powered. Listening initiated. Voice centers activated. Checking battery.")
    await general_utils.announce_battery_status()
    await weather_fetch.startup_fetch_forecast()
    startup_words = "This is so exciting! what are we doing today?"
    await actions_manager.startup_speech_actions(startup_words)

    while True:
        print("Entering the main loop, waiting for input...")
        spoken_text, raw_audio = await audio_input.recognize_speech_vosk(return_audio=True)  # Get input and raw audio

        # If no text was recognized, loop back and wait again
        if not spoken_text:
            # print("No input detected, waiting...")
            continue

        # Handle commands and check for any program-ending signals
        command_detected, should_exit = await command_manager.handle_command(spoken_text)
        if should_exit:
            break  # End the main loop if the command tells us to exit
        if command_detected:
            continue  # Command was detected and handled, go back to waiting for input

        # Otherwise, proceed with normal conversation
        stop_event = asyncio.Event()
        # Detect and play a sound based on user's emotion
        user_emotion = emotion_handler.analyze_text_emotion(spoken_text)
        # print(f"Detected user emotion: {user_emotion}")
        emotion_sound_manager.play_sound(user_emotion)

        recognized_speaker = voiceprint_manager.recognize_speaker(raw_audio)
        # print(f"Recognized speaker: {recognized_speaker}")

        system_prompt = get_system_prompt(recognized_speaker, user_emotion)

        # Label the user input for the model
        user_input_for_llm = f"{recognized_speaker}: {spoken_text}"
        print(f"{recognized_speaker}: {spoken_text}")
        # print(f"{recognized_speaker} emotion: {user_emotion}")

        # Handle passive actions while LLM processes
        thinking_task = asyncio.create_task(actions_manager.handle_passive_actions(stop_event))
        response_text = await llm_client.send_message_async(system_prompt, user_input_for_llm)
        stop_event.set()
        await thinking_task  # Wait for background actions to finish

        # Log the response to the file
        general_utils.log_response_to_file(response_text)

        # Detect Hal's emotion from the response and play the corresponding sound
        hal_emotion = emotion_handler.analyze_text_emotion(response_text)
        print(f"Hal: {response_text}")
        # print(f"Hal's emotion: {hal_emotion}")
        emotion_sound_manager.play_sound(hal_emotion)
        # Speak the response
        await response_manager.speak_with_dynamic_flite(response_text)


if __name__ == "__main__":
    asyncio.run(main())
