import asyncio
import warnings
warnings.simplefilter('ignore')
import os
# Explicitly clear any previously cached env variables
os.environ.clear()
from helpers.global_config import UNIFIED_API_GATEWAY
server_host = UNIFIED_API_GATEWAY

from mind.world_state_manager import WorldStateManager
from mind.internal_state_manager import InternalStateManager
from mind.perception_manager import PerceptionManager
from mind.decision_manager import DecisionManager
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
from mind.decision_manager import DecisionManager
from audio_output.emotional_sounds_manager import EmotionalSoundsManager
from audio_output.response_manager import Response_Manager
from helpers.gateway_server_client import GatewayClient
from eyes.EyeConfig import EyeConfig
from eyes.EyeExpressionManager import EyeExpressionManager
from eyes.EyeFrameComposer import EyeFrameComposer
from eyes.EyeGazeInterpolator import GazeInterpolator

# Hardware singletons
picrawler_instance = Picrawler()
searchlight = Searchlight()

# Actions (Picrawler is now the action manager)
actions_manager = picrawler_instance

# Eyes
eye_profile = EyeConfig.load_eye_profile("whitegold01")
composer = EyeFrameComposer(eye_profile)
gaze_interpolator = GazeInterpolator()
expression_manager = EyeExpressionManager()

composer.setup(gaze_interpolator, expression_manager)
gaze_interpolator.setup(composer)
expression_manager.setup(composer)

# Action + sound managers (must exist before MacroPlayer)
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
unified_server = GatewayClient(server_host)
world_state = WorldStateManager()
internal_state = InternalStateManager()
perception = PerceptionManager()

async def main():

    # --- Initialize subsystems ------------------------------------------------
    decision_manager = DecisionManager()
    audio_input = AudioInputManager(picrawler_instance)

    print("[Hal] Ready. Entering main loop.")

    # --- Main Loop -----------------------------------------------------------
    while True:

        # AUDIO INPUT ------------------------------------------------------
        raw_audio = await audio_input.capture_audio()

        if raw_audio is None or len(raw_audio) == 0:
            continue

        # TRANSCRIPTION (UNIFIED SERVER) -----------------------------------
        transcription = await unified_server.transcribe_audio(raw_audio)

        spoken_text = transcription.get("text", "")
        speaker = transcription.get("speaker", "Unknown")
        detected_emotion = transcription.get("emotion", "neutral")

        if not spoken_text:
            continue

        # PERCEPTION SNAPSHOT ----------------------------------------------
        perception.update(
            user_text=spoken_text,
            user_emotion=detected_emotion,
            speaker=speaker,
            battery_level=None,
            audio_direction=None,
            last_action=None,
            faces=[],
            objects=[],
            qr_codes=[],
        )

        # SEND TO UNIFIED SERVER (COGNITION) -------------------------------
        payload = {
            "world_state": world_state.snapshot(),
            "internal_state": internal_state.snapshot(),
            "perception": perception.snapshot(),
        }
        # PARSE SERVER RESPONSE --------------------------------------------
        try:
            server_json = await unified_server.send_perception(payload)
            server_intent = parse_server_intent(server_json)
        except Exception as e:
            print(f"[Server Error] {e}")
            server_intent = {"intent": "observe"}  # safe fallback
            
        # Ensure perception is reset for next loop 
        # (important for fields that may not be overwritten by server response)    
        perception.reset()

        # DECISION LAYER ----------------------------------------------------
        behavior_plan = decision_manager.decide(
            perception.snapshot(),
            server_intent
        )
        # PLAN → DSL --------------------------------------------------------
        dsl_script = behavior_plan_to_dsl(behavior_plan)

        # EXECUTE -----------------------------------------------------------
        if dsl_script.strip():
            await macro_player.run(dsl_script)

        # LOOP --------------------------------------------------------------
        await asyncio.sleep(0.01)