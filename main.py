import asyncio
import warnings
warnings.simplefilter('ignore')
import os
# Explicitly clear any previously cached env variables
os.environ.clear()
from helpers.global_config import UNIFIED_API_GATEWAY
import time

from mind.world_state_manager import WorldStateManager
from mind.internal_state_manager import InternalStateManager
from mind.perception_manager import PerceptionManager
from mind.decision_manager import DecisionManager, Perception
from mind.server_intent_parser import parse_server_intent
from dsl.behavior_plan_to_dsl import behavior_plan_to_dsl

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
from mind.decision_manager import DecisionManager
from audio_output.emotional_sounds_manager import EmotionalSoundsManager
from mind.emotions_manager import EmotionCategorizer
from audio_output.response_manager import Response_Manager
from helpers.weather_command_manager import WeatherCommandManager
from helpers.llm_client_handler import LLMClientHandler
from body.passive_actions_manager import PassiveActionsManager
from helpers.general_utilities_manager import GeneralUtilitiesManager
from helpers.news_handler import NewsHandler
from eyes.EyeConfig import EyeConfig
from eyes.EyeExpressionManager import EyeExpressionManager
from eyes.EyeFrameComposer import EyeFrameComposer
from eyes.EyeGazeInterpolator import GazeInterpolator

# Hardware singletons
picrawler_instance = Picrawler()
searchlight = Searchlight()

# Eyes
eye_profile = EyeConfig.load_eye_profile("whitegold01")
composer = EyeFrameComposer(eye_profile)
gaze_interpolator = GazeInterpolator()
expression_manager = EyeExpressionManager()

composer.setup(gaze_interpolator, expression_manager)
gaze_interpolator.setup(composer)
expression_manager.setup(composer)

# Action + sound managers (must exist before MacroPlayer)
actions_manager = PassiveActionsManager(picrawler_instance)
emotion_sound_manager = EmotionalSoundsManager()
response_manager = Response_Manager(picrawler_instance, actions_manager)
# MacroPlayer
macro_player = MacroPlayer(
    gaze=GazeChannel(gaze_interpolator),
    expression=ExpressionChannel(expression_manager),
    speech=SpeechChannel(response_manager),
    action=ActionChannel(actions_manager),
    sound=SoundChannel(emotion_sound_manager.play_sound)
)
server_host = UNIFIED_API_GATEWAY
unified_server = LLMClientHandler(server_host)
world_state = WorldStateManager()
internal_state = InternalStateManager()
perception = PerceptionManager()

async def main():

    # --- Initialize subsystems ------------------------------------------------
    decision_manager = DecisionManager()
    audio_input = AudioInputManager(picrawler_instance)
    voiceprint_manager = VoiceRecognitionManager()
    emotion_categorizer = EmotionCategorizer()
    unified_server = LLMClientHandler(server_host)

    print("[Hal] Ready. Entering main loop.")

    # --- Main Loop -----------------------------------------------------------
    while True:

        # 1. AUDIO INPUT ------------------------------------------------------
        spoken_text, raw_audio = await audio_input.recognize_speech_vosk(return_audio=True)

        if not spoken_text:
            continue

        # 2. PERCEPTION SNAPSHOT ----------------------------------------------
        speaker = voiceprint_manager.recognize_speaker(raw_audio)
        user_emotion = emotion_categorizer.analyze_text_emotion(spoken_text)

        perception.update(
            user_text=spoken_text,
            user_emotion=user_emotion,
            speaker=speaker
        )


        # 3. SEND TO UNIFIED SERVER -------------------------------------------
        server_payload = {
            "world_state": world_state.snapshot(),
            "internal_state": internal_state.snapshot(),
            "perception": perception.snapshot()
        }

        server_json = await unified_server.send_message_async(server_payload)

        # Ensure perception is reset for next loop 
        # (important for fields that may not be overwritten by server response)    
        perception.reset()

        # 4. PARSE SERVER RESPONSE --------------------------------------------
        server_intent = parse_server_intent(server_json)

        # 5. DECISION LAYER ----------------------------------------------------
        behavior_plan = decision_manager.decide(
            perception.snapshot(),
            server_intent
        )
        # 6. PLAN → DSL --------------------------------------------------------
        dsl_script = behavior_plan_to_dsl(behavior_plan)

        # 7. EXECUTE -----------------------------------------------------------
        if dsl_script.strip():
            await macro_player.run(dsl_script)

        # 8. LOOP --------------------------------------------------------------
        await asyncio.sleep(0.01)