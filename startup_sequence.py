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
from mind.emotional_sounds_manager import EmotionHandler, EmotionalSoundsManager
from helpers.weather_command_manager import WeatherCommandManager
from helpers.llm_client_handler import LLMClientHandler
from helpers.passive_actions_manager import PassiveActionsManager
from helpers.general_utilities_manager import GeneralUtilitiesManager
from helpers.news_handler import NewsHandler
from eyes.eye_loader import load_eye_profile
from eyes.eye_animator import EyeAnimator
from eyes.eye_expression_manager import EyeExpressionManager
from eyes.core.blink_engine import BlinkEngine
from eyes.eye_frame_composer import EyeFrameComposer

# Initialize everything at module level
eye_profile = load_eye_profile("vector03")
eye_animator = EyeAnimator(eye_profile)
blink_engine = BlinkEngine(eye_animator)
expression_manager = EyeExpressionManager(eye_animator)
composer = EyeFrameComposer(eye_animator, expression_manager, blink_engine)
server_host = OLLAMALAPTOP
llm_client = LLMClientHandler(server_host)
voiceprint_manager = VoiceRecognitionManager()
command_manager = CommandManager(llm_client, picrawler_instance, eye_animator)
audio_input = AudioInputManager(picrawler_instance)
emotion_handler = EmotionHandler()
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
    print("Starting BlinkEngine loop.")
    asyncio.create_task(composer.start_idle_blink_loop())
    print("Starting EyeFrameComposer loop.")
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
        speak "Beginning sound output test."
        wait 0.5
        sound disgust
        wait 0.5
        speak "Sound output active."
        wait 0.5
        speak "Testing servos."
        wait 0.5
        action expressive
        wait 0.5
        speak "Servos active. Interactive Visual Display initiating."
        """)
    
    await macro_player.run(
        """
        gaze move to 10 20 1.5
        wait 2
        speak " expression is now test. "
        expression set mood test
        wait 4
        speak " expression is now sleepy. "
        expression set mood sleepy
        wait 4
        speak " expression is now test. "
        expression set mood test
        wait 4
        expression set mood neutral
        wait 2
        gaze move to 10 10 1.0
        wait 2
        """
    )
    await macro_player.run(
        """
        speak "Interactive Visual Display active. Camera active. Gaze tracking active."
        wait 5
        speak "Listening active. Voiceprint recognition active."
        wait 2
        """)
    # remaining startup sequence with Battery and News/Weather fetch removed until rewritten

    while True:
        print("Entering the main loop, waiting for input...")
        await macro_player.run(f"""
                               wait 2
                               gaze move to 15 10 1.0
                               wait 2
                               gaze move to 10 15 1.0
                               wait 2
                               gaze move to 10 10 1.0
                               """)
        spoken_text, raw_audio = await audio_input.recognize_speech_vosk(return_audio=True)  # Get input and raw audio
        
        if not spoken_text:  # If no text was recognized, loop back and wait again
            continue
        # Verbal Command Handler removed until rewritten
        # ThinkingTask loop removed for testing and because new model is superfast

        # Detect and play a sound based on user's emotion
        user_emotion = emotion_handler.analyze_text_emotion(spoken_text)
        await macro_player.run(f"sound {user_emotion}")

        recognized_speaker = voiceprint_manager.recognize_speaker(raw_audio)

        # Label the user input for the model
        user_input_for_llm = f"{recognized_speaker}: {spoken_text}"
        print(f"{recognized_speaker}: emotion: {user_emotion}\n{spoken_text}")

        response_text = await llm_client.send_message_async(user_input_for_llm)
        # Detect Hal's emotion from the response and play the corresponding sound
        hal_emotion = emotion_handler.analyze_text_emotion(response_text)
        await macro_player.run(f"""
            expression set mood {hal_emotion}
            sound {hal_emotion}
            action expressive
        """)
        # Perform the response sequence
        macro_script = TagToDSL.parse(response_text)
        await macro_player.run(macro_script)

if __name__ == "__main__":
    asyncio.run(main())
