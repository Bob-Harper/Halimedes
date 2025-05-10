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
from dsl.channels import GazeChannel, ExpressionChannel, SpeechChannel, ActionChannel, SoundChannel
from dsl.macro_player import MacroPlayer, TagToDSL
from helpers.response_manager import Response_Manager
from helpers.audio_input_manager import AudioInputManager
from audio_input.verbal_commands import CommandManager
from audio_input.voice_recognition_manager import VoiceRecognitionManager
from helpers.emotional_sounds_manager import EmotionHandler, EmotionalSoundsManager
from helpers.weather_command_manager import WeatherCommandManager
#from helpers.prompt_template_manager import PromptTemplateManager
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
# template_manager = PromptTemplateManager(model_name="gemma3:1b")
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
macro_player = MacroPlayer(
    gaze=GazeChannel(eye_animator),
    expression=ExpressionChannel(eye_animator),
    speech=SpeechChannel(response_manager),
    action=ActionChannel(actions_manager),
    sound=SoundChannel(emotion_sound_manager.play_sound)
)


async def main():
    print("Entered main()")
    await macro_player.run(
        """
        speak "Gaze tracking initiated. Eye animation system online."
        wait 1.0
        speak "Listening initiated. Voiceprint recognition active. Voice centers activated. Checking battery."
        """)
    await macro_player.run(
        """
        expression set mood closed
        expression set mood test
        gaze move to 10 10 2.0
        wait 0.3
        expression set mood test2
        gaze move to 10 10 0.3
        wait 0.3
        expression set mood neutral
        gaze move to 10 10 1.0
        """)    
    await macro_player.run(
        """
        speak "Beginning startup procedure and status check. Please stand by, system test underway."
        wait 1.0
        speak "Servos powered. Camera online. Interactive Visual Display initiating."
        """)
    # NOTE THE ENTIRE FOLLOWING PORTION RELIES ON EXTERNAL FILES AND CLASSES NOT YET SEQUENCED
    # await general_utils.announce_battery_status()  # need to update class to hande Macro Player
    # await weather_fetch.startup_fetch_forecast()  # need to update class to hande Macro Player
    # startup_news_item = await news_api.startup_fetch_news(llm_client)
    # current_time = news_api.current_datetime()
    # await response_manager.speak_with_flite(f"Today's date is {current_time}.", emotion="announcement") 
    # await eye_animator.set_expression("surprised") 
    # startup_words = "This is so exciting! What shall we talk about today?"
    # await actions_manager.startup_speech_actions(startup_words)
    # if startup_news_item:
    #     await eye_animator.set_expression("happy")
    #     conversation_starter = f"Oh, I know! Did you hear about this? {startup_news_item}"
    #     await response_manager.speak_with_flite(conversation_starter, emotion="announcement")
    # NOTE DO NOT RE_ENABLE UNTIL THE ABOVE IS FIXED

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
            await macro_player.run(
                """
                expression set mood closed
                """)
            break  # End the main loop if the command tells us to exit
        if command_detected:
            continue  # Command was detected and handled, go back to waiting for input

        # Otherwise, proceed with normal conversation
        stop_event = asyncio.Event()
        # Detect and play a sound based on user's emotion
        user_emotion = emotion_handler.analyze_text_emotion(spoken_text)
        await macro_player.run(f"sound {user_emotion}")

        recognized_speaker = voiceprint_manager.recognize_speaker(raw_audio)

        # Label the user input for the model
        user_input_for_llm = f"{recognized_speaker}: {spoken_text}"
        print(f"{recognized_speaker}: emotion: {user_emotion}\n{spoken_text}")

        # Handle passive actions while LLM processes
        thinking_task = asyncio.create_task(actions_manager.handle_passive_actions(stop_event))
        response_text = await llm_client.send_message_async(user_input_for_llm)
        stop_event.set()
        await thinking_task

        # Detect Hal's emotion from the response and play the corresponding sound
        hal_emotion = emotion_handler.analyze_text_emotion(response_text)
        print(f"Hal: {response_text}")
        print(f"Hal's emotion: {hal_emotion}")
        await macro_player.run(f"""
            expression set mood {hal_emotion}
            sound {hal_emotion}
            action expressive
        """)
        # Speak the response
        macro_script = TagToDSL.parse(response_text)
        print("Generated DSL:\n", macro_script)  # Debug view
        await macro_player.run(macro_script)

if __name__ == "__main__":
    asyncio.run(main())
