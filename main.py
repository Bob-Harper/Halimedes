from crawler_utils.utils import reset_mcu
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

from cortex.decision_manager import DecisionManager
from cortex.world_state_manager import WorldStateManager
from cortex.internal_state_manager import InternalStateManager
from cortex.perception_manager import PerceptionManager
from cortex.context_builder import ContextBuilder
from cortex.initiative_manager import InitiativeManager
from cortex.action_executor import ActionExecutor
from cortex.cognition_loop import CognitionLoop
from cortex.server_intent_parser import parse_server_intent
from body.searchlight import Searchlight
from audio_input.audio_input_manager import AudioInputManager
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
audio_input = AudioInputManager(picrawler_instance)

unified_server = GatewayClient(server_host)
world_state = WorldStateManager()
internal_state = InternalStateManager()
perception = PerceptionManager()
decision_manager = DecisionManager()
context_builder = ContextBuilder()
initiative_manager = InitiativeManager()
action_executor = ActionExecutor(
    motors=actions_manager,
    eyes=expression_manager,
    searchlight=searchlight,
    audio=response_manager
)

cortex = CognitionLoop(
    perception_manager=perception,
    context_builder=context_builder,
    initiative_manager=initiative_manager,
    decision_manager=decision_manager,
    action_executor=action_executor,
    tick_rate=0.1
)
async def main():

    print("[Hal] Ready. Entering main loop.")
    print("[Hal] Listening.")
    while True:

        # AUDIO INPUT ------------------------------------------------------
        pcm_audio = await audio_input.capture_audio()
        if pcm_audio is None or len(pcm_audio) == 0:
            continue

        # --- AUDIO SAFETY CAP --------------------------------------------
        MAX_AUDIO_BYTES = 5_000_000  # ~5 MB cap
        truncated = False

        # pcm_audio is int16 → 2 bytes per sample
        if pcm_audio.nbytes > MAX_AUDIO_BYTES:
            print(f"[Audio] Oversized capture ({pcm_audio.nbytes} bytes). Truncating.")
            max_samples = MAX_AUDIO_BYTES // 2
            pcm_audio = pcm_audio[:max_samples]
            truncated = True

        print(f"[Audio] Captured {pcm_audio.nbytes} bytes")

        raw_bytes = pcm_audio.tobytes()
        transcription = await unified_server.transcribe_audio(raw_bytes)

        # transcription = await unified_server.transcribe_audio(wav_bytes)
        print(f"[Transcription RAW] {transcription}")
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
            truncated=truncated,
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
        cortex.tick(server_intent)
        print(f"[Decision] Executed plan for intent '{server_intent.get('intent')}'")
        # LOOP --------------------------------------------------------------
        print("[Hal] Listening.")
        await asyncio.sleep(0.01)

async def graceful_shutdown():

    print("[Shutdown] Resetting MCU...")
    reset_mcu()

    print("[Shutdown] Done.")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("[Shutdown] KeyboardInterrupt received.")
        asyncio.run(graceful_shutdown())
    except Exception as e:
        print(f"[Shutdown] Fatal error: {e}")
        asyncio.run(graceful_shutdown())
        raise

