# STARTUP.PY AUTOSTART SERVICE IS DISABLED, HAL WILL BOOT STRAIGHT INTO CODE MODE
import asyncio
import warnings
warnings.simplefilter('ignore')
import os
os.environ.clear()
from helpers.global_config import OLLAMASERVER
""" 
NOTE Import the Picrawler class first to pass through.
This prevents multiple initializations of the Picrawler class.
"""
from body.picrawler import Picrawler 
picrawler_instance = Picrawler()
# NOTE we now have a single instance of Picrawler to pass through
from dsl.channels import GazeChannel, ExpressionChannel, SpeechChannel, ActionChannel, SoundChannel
from dsl.macro_player import MacroPlayer
from helpers.response_manager import Response_Manager
from audio_input.audio_input_manager import AudioInputManager
from audio_input.verbal_commands import CommandManager
from audio_input.voice_recognition_manager import VoiceRecognitionManager
from mind.emotional_sounds_manager import EmotionalSoundsManager
from mind.emotions_manager import EmotionCategorizer
from helpers.llm_client_handler import LLMClientHandler
from helpers.passive_actions_manager import PassiveActionsManager
from helpers.general_utilities_manager import GeneralUtilitiesManager
from eyes.EyeConfig import EyeConfig
from eyes.EyeExpressionManager import EyeExpressionManager
from eyes.EyeFrameComposer import EyeFrameComposer
from eyes.EyeGazeInterpolator import GazeInterpolator

# Initialize everything at module level
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
actions_manager = PassiveActionsManager(picrawler_instance)
response_manager = Response_Manager(picrawler_instance, actions_manager)
general_utils = GeneralUtilitiesManager(picrawler_instance)

macro_player = MacroPlayer(
    gaze=GazeChannel(gaze_interpolator),
    expression=ExpressionChannel(expression_manager),
    speech=SpeechChannel(response_manager),
    action=ActionChannel(actions_manager),
    sound=SoundChannel(emotion_sound_manager.play_sound)
)


async def main():
    print("Entered main()")
    asyncio.create_task(composer.start_loop())  
  
    # NOTE macros may be broken into multiple sequences for a reason during debugging.  
    # leave them this way. do not consolidate..
    
    await macro_player.run(
        """
        expression set mood sleepy
        gaze move to 90 90 1.0
        wait 1.2
        expression set mood neutral
        gaze move to 100 90 1.0
        wait 1.2
        expression set mood sleepy
        gaze move to 80 90 1.0
        wait 1.2
        expression set mood positive
        gaze move to 90 90 1.0
        wait 1.2
        expression set mood negative
        gaze move to 90 100 1.0
        wait 1.2
        expression set mood joy
        gaze move to 90 80 1.0
        wait 1.2
        expression set mood surprise
        gaze move to 90 90 1.0
        gaze move to 90 90 1.0
        wait 1.2
        expression set mood neutral
        gaze move to 100 90 1.0
        wait 1.2
        expression set mood sleepy
        gaze move to 80 90 1.0
        wait 1.2
        expression set mood positive
        gaze move to 90 90 1.0
        wait 1.2
        expression set mood negative
        gaze move to 90 100 1.0
        wait 1.2
        expression set mood joy
        gaze move to 90 80 1.0
        wait 1.2
        expression set mood surprise
        gaze move to 90 90 1.0
        gaze move to 90 90 1.0
        wait 1.2
        expression set mood neutral
        gaze move to 100 90 1.0
        wait 1.2
        expression set mood sleepy
        gaze move to 80 90 1.0
        wait 1.2
        expression set mood positive
        gaze move to 90 90 1.0
        wait 1.2
        expression set mood negative
        gaze move to 90 100 1.0
        wait 1.2
        expression set mood joy
        gaze move to 90 80 1.0
        wait 1.2
        expression set mood surprise
        gaze move to 90 90 1.0

        """
    )    

    print("Macro complete. Shutting down render loops.")

if __name__ == "__main__":
    asyncio.run(main())
