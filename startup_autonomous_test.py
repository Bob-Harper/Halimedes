# STARTUP.PY AUTOSTART SERVICE IS DISABLED.  
# This must be started Manually until the new autonomous decision making layer 
# is fully implemented and tested.  
# HAL will boot straight into code mode. This file uses a simplified startup sequence 
# before entering the main loop.  
# Once the new system is fully tested and stable, we can re-enable the autostart service 
# and rename this file, then designate it as the default on-boot startup.
# Autonomous Decision Making Layer Testing Enabled.
import asyncio
import warnings
warnings.simplefilter('ignore')
import os
# Explicitly clear any previously cached env variables
os.environ.clear()
from helpers.global_config import OLLAMASERVER
import time
""" 
NOTE Import the Picrawler class first to pass through.
This prevents multiple initializations of the Picrawler class.
"""
from body.picrawler import Picrawler 
picrawler_instance = Picrawler()
# NOTE we now have a single instance of Picrawler to pass through
from body.searchlight import Searchlight
from dsl.channels import GazeChannel, ExpressionChannel, SpeechChannel, ActionChannel, SoundChannel
from dsl.macro_player import MacroPlayer
from audio_input.audio_input_manager import AudioInputManager
from audio_input.verbal_commands import CommandManager
from audio_input.voice_recognition_manager import VoiceRecognitionManager
from mind.decision_manager import DecisionManager, Intent
from audio_output.speech_interaction_manager import SpeechInteractionManager
from audio_output.emotional_sounds_manager import EmotionalSoundsManager
from mind.emotions_manager import EmotionCategorizer
from audio_output.response_manager import Response_Manager
from helpers.weather_command_manager import WeatherCommandManager
from helpers.llm_client_handler import LLMClientHandler
from body.passive_actions_manager import PassiveActionsManager
from body.locomotion_manager import LocomotionManager
from helpers.general_utilities_manager import GeneralUtilitiesManager
from helpers.news_handler import NewsHandler
from eyes.EyeConfig import EyeConfig
from eyes.EyeExpressionManager import EyeExpressionManager
from eyes.EyeFrameComposer import EyeFrameComposer
from eyes.EyeGazeInterpolator import GazeInterpolator

# Initialize everything at module level
decision_manager = DecisionManager()
eye_profile = EyeConfig.load_eye_profile("whitegold01")
composer = EyeFrameComposer(eye_profile)
gaze_interpolator = GazeInterpolator()
expression_manager = EyeExpressionManager()
composer.setup(gaze_interpolator, expression_manager)
gaze_interpolator.setup(composer)
expression_manager.setup(composer)
server_host = OLLAMASERVER
llm_client = LLMClientHandler(server_host)
voiceprint_manager = VoiceRecognitionManager()
command_manager = CommandManager(llm_client, picrawler_instance)
audio_input = AudioInputManager(picrawler_instance)
emotion_categorizer = EmotionCategorizer()
emotion_sound_manager = EmotionalSoundsManager()
active_actions_manager = LocomotionManager(picrawler_instance)
passive_actions_manager = PassiveActionsManager(picrawler_instance)
response_manager = Response_Manager(picrawler_instance, passive_actions_manager)
general_utils = GeneralUtilitiesManager(picrawler_instance)
weather_fetch = WeatherCommandManager(llm_client, passive_actions_manager, emotion_sound_manager, picrawler_instance)
news_api = NewsHandler(picrawler_instance)
macro_player = MacroPlayer(
    gaze=GazeChannel(gaze_interpolator),
    expression=ExpressionChannel(expression_manager),
    speech=SpeechChannel(response_manager),
    action=ActionChannel(passive_actions_manager),
    sound=SoundChannel(emotion_sound_manager.play_sound)
)
searchlight = Searchlight()
speech_manager = SpeechInteractionManager(
    emotion_categorizer,
    macro_player,
    voiceprint_manager,
    llm_client
)


async def main():
    tasks = asyncio.all_tasks()
    print(f"[Startup] Pre-main task count: {len(tasks)}")

    for t in tasks:
        coro = t.get_coro()
        coro_name = getattr(coro, '__name__', repr(coro))
        print(f"[Startup] Task: {coro_name}, done={t.done()}, cancelled={t.cancelled()}")
    print("[Startup] Starting main sequence...")
    asyncio.create_task(composer.start_loop())  
    # NOTE these are broken into multiple sequences for a reason.  
    # leave them this way. do not consolidate at this time.
    await macro_player.run(
        """
        speak "Beginning startup procedure and status check. Please stand by, system test underway."
        wait 0.5
        speak "beginning Speech output test."
        wait 0.5
        speak "Speech output active."
        wait 0.5
        speak "Obviously."
        wait 0.5
        speak "Beginning sound effect output test."
        wait 0.5
        sound disgust
        wait 0.5
        speak "Sound effect output active."
        wait 0.5
        speak "Testing servos."
        wait 0.5
        action expressive
        wait 0.5
        action sit
        wait 0.5
        speak "Servos active. Testing shoulder mounted photon projector."
        """)
    searchlight.brightness(10)
    time.sleep(0.1)
    searchlight.brightness(1)
    time.sleep(0.5)
    searchlight.brightness(100)
    time.sleep(0.1)
    searchlight.brightness(0)
    await macro_player.run(
        """
        speak "Photon Projector active.  "
        wait 1
        speak "Interactive Visual Display initiating."
        gaze move to 80 100
        wait 2
        speak " expression is now test. "
        expression set mood test
        wait 2
        speak " expression is now sleepy. "
        expression set mood sleepy
        gaze move to 100 80
        wait 2
        speak " expression is now test. "
        expression set mood test
        wait 2
        expression set mood neutral
        wait 2
        gaze move to 90 90
        wait 2
        """
    )
    await macro_player.run(
        """
        speak "Interactive Visual Display active. Camera active. Gaze tracking active."
        wait 2
        speak "Listening active. Voiceprint recognition active."
        """)
        #     await general_utils.announce_battery_status()
        #     await weather_fetch.startup_fetch_forecast()
        #     startup_news_item = await news_api.startup_fetch_news(llm_client)
        #     current_time = news_api.current_datetime()
        #     await response_manager.speak_with_flite(f"Today's date is {current_time}.", emotion="announcement") 
        #     await eye_animator.set_expression("surprised") 
        #     startup_words = "This is so exciting! What shall we talk about today?"
        #     await actions_manager.startup_speech_actions(startup_words)
        #     if startup_news_item:
        #         await eye_animator.set_expression("happy")
        #         conversation_starter = f"Oh, I know! Did you hear about this? {startup_news_item}"
        #         await response_manager.speak_with_flite(conversation_starter, emotion="announcement")

    while True:
        print("Entering the main loop, waiting for input...")

        spoken_text, raw_audio = await audio_input.recognize_speech_vosk(return_audio=True)

        if spoken_text:
            sensory_event = {
                "type": "speech",
                "data": {
                    "text": spoken_text,
                    "audio": raw_audio
                }
            }
        else:
            sensory_event = {"type": "silence", "data": None}

        intent = decision_manager.decide(sensory_event)

        if intent == Intent.RESPOND_TO_USER and spoken_text:
            await speech_manager.handle_speech(spoken_text, raw_audio)

        elif intent == Intent.PERFORM_IDLE_BEHAVIOR:
            await passive_actions_manager.perform_idle_behavior()

        elif intent == Intent.INVESTIGATE_SOUND:
            await active_actions_manager.look_toward_sound()

        else:
            await passive_actions_manager.idle_tick()

                    
if __name__ == "__main__":
    asyncio.run(main())
