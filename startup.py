# STARTUP.PY AUTOSTART SERVICE IS DISABLED, HAL WILL BOOT STRAIGHT INTO WORK MODE
import asyncio
import warnings
warnings.simplefilter('ignore')
import asyncio
from helpers.global_config import OLLAMALAPTOP
""" 
Import the Picrawler class from the picrawler module first 
to pass through to all helper classes that use it.  This
prevents multiple initializations of the Picrawler class.
"""
from body.picrawler import Picrawler 
# Create a single instance of Picrawler to pass through
picrawler_instance = Picrawler()
from helpers.response_manager import Response_Manager
from helpers.audio_input_manager import AudioInputManager
from audio_input.verbal_commands import CommandManager
from audio_input.voice_recognition_manager import VoiceRecognitionManager
from helpers.emotional_sounds_manager import EmotionHandler, EmotionalSoundsManager
from helpers.weather_command_manager import WeatherCommandManager
from helpers.prompt_template_manager import PromptTemplateManager
from helpers.llm_client_handler import LLMClientHandler
from helpers.passive_actions_manager import PassiveActionsManager
from helpers.system_prompt_fetch import system_prompt_fetch
from helpers.general_utilities_manager import GeneralUtilitiesManager
from helpers.news_handler import NewsHandler
from eyes.eye_animator import EyeAnimator
from eyes.eye_loader import load_eye_profile
from eyes.core.blink_engine import BlinkEngine

# Initialize everything at module level
eye_profile = load_eye_profile("vector03")
eye_animator = EyeAnimator(eye_profile)
blinker = BlinkEngine(eye_animator)
template_manager = PromptTemplateManager(model_name="gemma3:1b")
llm_client = LLMClientHandler(server_host=OLLAMALAPTOP)
voiceprint_manager = VoiceRecognitionManager()
command_manager = CommandManager(llm_client, picrawler_instance, eye_animator)
audio_input = AudioInputManager(picrawler_instance)
emotion_handler = EmotionHandler()
emotion_sound_manager = EmotionalSoundsManager()
actions_manager = PassiveActionsManager(picrawler_instance)
response_manager = Response_Manager(picrawler_instance, actions_manager, eye_animator)  # Set once
general_utils = GeneralUtilitiesManager(picrawler_instance)
weather_fetch = WeatherCommandManager(llm_client, actions_manager, emotion_sound_manager, picrawler_instance)
news_api = NewsHandler(picrawler_instance)


async def main():
    print("Entered main()")
    await response_manager.speak_with_flite("Beginning startup procedure and status check. Please stand by, system test underway.")
    await response_manager.speak_with_flite("Servos powered. Camera online. Interactive Visual Display initiating.")

    # 1) Generate your first eye image in memory
    initial_buf = eye_animator.drawer.generate_frame(
        x_off=10,
        y_off=10,
        pupil_size=1.0
    )
    # Stash it so blink engine can find it
    eye_animator.last_buf = initial_buf
    # 2) Open from black straight into that buffer
    blinker.dual_blink_open(initial_buf, speed=0.3)
    # 3) Let the background blink loop start up
    asyncio.create_task(blinker.idle_blink_loop())

    eye_animator.draw_gaze(10, 10, pupil=2.0)
    await eye_animator.set_expression("test")
    eye_animator.draw_gaze(10, 10, pupil=0.3)
    await eye_animator.set_expression("test2")
    eye_animator.draw_gaze(10, 10, pupil=1.0)
    await eye_animator.set_expression("neutral")
    # Start the passive blink loop
    asyncio.create_task(blinker.idle_blink_loop())

    await response_manager.speak_with_flite("Gaze tracking initiated. Eye animation system online.")
    await response_manager.speak_with_flite("Listening initiated. Voiceprint recognition active. Voice centers activated. Checking battery.")
    await general_utils.announce_battery_status()
    await weather_fetch.startup_fetch_forecast()
    startup_news_item = await news_api.startup_fetch_news(llm_client)
    current_time = news_api.current_datetime()
    await response_manager.speak_with_flite(f"Today's date is {current_time}.", emotion="announcement") 
    await eye_animator.set_expression("surprised") 
    startup_words = "This is so exciting! What shall we talk about today?"
    await actions_manager.startup_speech_actions(startup_words)
    if startup_news_item:
        await eye_animator.set_expression("happy")
        conversation_starter = f"Oh, I know! Did you hear about this? {startup_news_item}"
        await response_manager.speak_with_flite(conversation_starter, emotion="announcement")

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
            blinker.dual_blink_close(speed=0.3)
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

        system_prompt = await system_prompt_fetch(recognized_speaker, user_emotion)

        # Label the user input for the model
        user_input_for_llm = f"{recognized_speaker}: {spoken_text}"
        print(f"{recognized_speaker}: emotion: {user_emotion}\n{spoken_text}")

        # Use PromptTemplateManager to wrap prompt properly for this model
        # final_prompt = template_manager.build_prompt(user_input_for_llm)

        # Handle passive actions while LLM processes
        await eye_animator.set_expression("focused")
        thinking_task = asyncio.create_task(actions_manager.handle_passive_actions(stop_event))
        # response_text = await llm_client.send_message_async(system_prompt, final_prompt)  # with prompt manager
        response_text = await llm_client.send_message_async(user_input_for_llm)  # without prompt manager
        stop_event.set()
        await thinking_task  # Wait for background actions to finish

        # Log the response to the file
        general_utils.log_response_to_file(response_text)

        # Detect Hal's emotion from the response and play the corresponding sound
        hal_emotion = emotion_handler.analyze_text_emotion(response_text)
        print(f"Hal: {response_text}")
        # print(f"Hal's emotion: {hal_emotion}")
        # await eye_animator.set_expression("hal_emotion")
        emotion_sound_manager.play_sound(hal_emotion)
        # Speak the response
        await response_manager.fully_dynamic_response(response_text)

if __name__ == "__main__":
    asyncio.run(main())
