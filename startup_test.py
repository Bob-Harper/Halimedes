# STARTUP.PY AUTOSTART SERVICE IS DISABLED, HAL WILL BOOT STRAIGHT INTO CODE MODE
import asyncio
import warnings
warnings.simplefilter('ignore')
import os
# Explicitly clear any previously cached env variables
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
print("Initializing components...")
eye_profile = EyeConfig.load_eye_profile("whitegold01")
print("Eye profile loaded.")
composer = EyeFrameComposer(eye_profile, None, None)
gaze_interpolator = GazeInterpolator(composer)
expression_manager = EyeExpressionManager(composer)

composer.gaze_interpolator = gaze_interpolator
composer.expression_manager = expression_manager
gaze_interpolator.composer = composer
expression_manager.composer = composer

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
print(f"[Debug] composer: {id(composer)}")
print(f"[Debug] expression_manager.composer: {id(expression_manager.composer)}")
print(f"[Debug] gaze_interpolator.composer: {id(gaze_interpolator.composer)}")


async def main():
    print("Entered main()")
    print(">>>> STARTING MAIN")
    try:
        await expression_manager.set_expression("test2")
        print("[Startup] Expression set to 'test2'")
    except Exception as e:
        print(f"[Startup] CRASHED in set_expression: {e}")


    print("Starting EyeFrameComposer loop.")
    asyncio.create_task(composer.start_loop())  
  
    # NOTE macros may be broken into multiple sequences for a reason during debugging.  
    # leave them this way. do not consolidate..
    
    await macro_player.run(
        """
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
    print(">>>> END OF MAIN")

if __name__ == "__main__":
    print(__file__)
    print("Running from", __name__)
    asyncio.run(main())
