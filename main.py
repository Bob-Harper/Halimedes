from utils.utils import reset_mcu
import asyncio
import warnings
warnings.simplefilter('ignore')
import os
# Explicitly clear any previously cached env variables
os.environ.clear()
from helpers.global_config import UNIFIED_API_GATEWAY
server_host = UNIFIED_API_GATEWAY
""" 
NOTE Import the Picrawler class first to pass through.
This prevents multiple initializations of the Picrawler class.
Multiple implementation is NOT harmless, it is 100% disruptive.
"""
from body.picrawler import Picrawler 
picrawler_instance = Picrawler()
# We now have a single instance of Picrawler to pass to other classes that require it.

from mind.world_state_manager import WorldStateManager
from mind.internal_state_manager import InternalStateManager
from mind.perception_manager import PerceptionManager
from mind.decision_manager import DecisionManager
from mind.server_intent_parser import parse_server_intent
from dsl.behavior_plan_to_dsl import behavior_plan_to_dsl
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

    print("[Init] Starting subsystem initialization…")

    decision_manager = DecisionManager()
    audio_input = AudioInputManager(picrawler_instance)

    print("[Init] Subsystems ready.")
    print("[Hal] Ready. Entering main loop.")

    while True:

        # AUDIO INPUT ------------------------------------------------------
        raw_audio = await audio_input.capture_audio()
        if raw_audio is None or len(raw_audio) == 0:
            continue

        print(f"[Audio] Captured {len(raw_audio)} bytes")

        # TRANSCRIPTION ----------------------------------------------------
        transcription = await unified_server.transcribe_audio(raw_audio)

        spoken_text = transcription.get("text", "")
        speaker = transcription.get("speaker", "Unknown")
        detected_emotion = transcription.get("emotion", "neutral")

        print(f"[Transcription] text='{spoken_text}' speaker='{speaker}' emotion='{detected_emotion}'")

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

        print(f"[Perception] Snapshot updated: {perception.snapshot()}")

        # SEND TO UNIFIED SERVER (COGNITION) -------------------------------
        payload = {
            "world_state": world_state.snapshot(),
            "internal_state": internal_state.snapshot(),
            "perception": perception.snapshot(),
        }

        print("[Cognition] Sending perception to server…")

        try:
            server_json = await unified_server.send_perception(payload)
            server_intent = parse_server_intent(server_json)
            print(f"[Cognition] Server intent: {server_intent}")
        except Exception as e:
            print(f"[Server Error] {e}")
            server_intent = {"intent": "observe"}

        # RESET PERCEPTION -------------------------------------------------
        perception.reset()

        # DECISION LAYER ---------------------------------------------------
        behavior_plan = decision_manager.decide(
            perception.snapshot(),
            server_intent
        )

        print(f"[Decision] Behavior plan: {behavior_plan}")

        # PLAN → DSL -------------------------------------------------------
        dsl_script = behavior_plan_to_dsl(behavior_plan)
        print(f"[DSL] Script generated: '{dsl_script.strip()}'")

        # EXECUTE ----------------------------------------------------------
        if dsl_script.strip():
            print("[Action] Executing DSL script…")
            await macro_player.run(dsl_script)

        # LOOP --------------------------------------------------------------
        await asyncio.sleep(0.01)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        reset_mcu()
    except Exception as e:
        print("Crash:", e)
        reset_mcu()
        raise

