# STARTUP.PY AUTOSTART SERVICE IS DISABLED, HAL WILL BOOT STRAIGHT INTO CODE MODE
import asyncio
import warnings
warnings.simplefilter('ignore')
import os
# Explicitly clear any previously cached env variables
os.environ.clear()
from helpers.global_config import OLLAMALAPTOP
""" 
NOTE Import the Picrawler class first to pass through.
This prevents multiple initializations of the Picrawler class.
"""
from body.picrawler import Picrawler 
picrawler_instance = Picrawler()
# NOTE we now have a single instance of Picrawler to pass through
from dsl.channels import GazeChannel, ExpressionChannel, SpeechChannel, ActionChannel, SoundChannel
from dsl.macro_player import MacroPlayer, TagToDSL
from helpers.response_manager import Response_Manager
from audio_input.audio_input_manager import AudioInputManager
from audio_input.verbal_commands import CommandManager
from audio_input.voice_recognition_manager import VoiceRecognitionManager
from mind.emotional_sounds_manager import EmotionalSoundsManager
from mind.emotions_manager import EmotionCategorizer
from helpers.weather_command_manager import WeatherCommandManager
from helpers.llm_client_handler import LLMClientHandler
from helpers.passive_actions_manager import PassiveActionsManager
from helpers.general_utilities_manager import GeneralUtilitiesManager
from helpers.news_handler import NewsHandler
from eyes.eye_frame_composer import load_eye_profile
from eyes.eye_frame_composer import EyeAnimator
from eyes.eye_frame_composer import EyeExpressionManager
from eyes.eye_frame_composer import EyeFrameComposer

# Initialize everything at module level
eye_profile = load_eye_profile("vector03")
eye_animator = EyeAnimator(eye_profile)
expression_manager = EyeExpressionManager(eye_animator)
composer = EyeFrameComposer(eye_animator, expression_manager)
server_host = OLLAMALAPTOP
llm_client = LLMClientHandler(server_host)
voiceprint_manager = VoiceRecognitionManager()
command_manager = CommandManager(llm_client, picrawler_instance, eye_animator)
audio_input = AudioInputManager(picrawler_instance)
emotion_categorizer = EmotionCategorizer()
emotion_sound_manager = EmotionalSoundsManager()
actions_manager = PassiveActionsManager(picrawler_instance)
response_manager = Response_Manager(picrawler_instance, actions_manager, eye_animator)
general_utils = GeneralUtilitiesManager(picrawler_instance)
weather_fetch = WeatherCommandManager(llm_client, actions_manager, emotion_sound_manager, picrawler_instance)
news_api = NewsHandler(picrawler_instance)
macro_player = MacroPlayer(
    gaze=GazeChannel(composer),
    expression=ExpressionChannel(composer),
    speech=SpeechChannel(response_manager),
    action=ActionChannel(actions_manager),
    sound=SoundChannel(emotion_sound_manager.play_sound)
)


async def main():
    print("Entered main()")
    print("Starting EyeFrameComposer loop.")
    asyncio.create_task(composer.start_loop())  
    print("Starting BlinkEngine loop.")
    # asyncio.create_task(composer.start_idle_blink_loop()) #expression changes power the blinks now
   
    # NOTE these are broken into multiple sequences for a reason.  
    # leave them this way. do not consolidate at this time.
    
    await macro_player.run(
        """
        gaze move to 10 20 1.5
        wait 2
        speak " expression is now test. "
        expression set mood test
        
        wait 6
        speak " expression is now positive. "
        gaze move to 10 5 0.9
        expression set mood positive
        wait 5
        speak " expression is now negative. "
        gaze move to 20 20 1.3
        expression set mood negative
        wait 5
        expression set mood neutral
        wait 4
        gaze move to 10 10 1.0
        wait 2
        expression set mood closed
        expression set mood neutral
        wait 5
        expression set mood closed
        expression set mood negative
        wait 5
        expression set mood closed
        expression set mood neutral
        wait 5
        expression set mood closed

        """
    )

    print("Macro complete. Shutting down render loops.")


if __name__ == "__main__":
    asyncio.run(main())
