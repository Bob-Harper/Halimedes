from crawler_utils.utils import reset_mcu
import asyncio
import warnings
warnings.simplefilter('ignore')
import os
# Explicitly clear any previously cached env variables
os.environ.clear()
from helpers.global_config import LED_INDICATOR
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
from cortex.emotions_manager import EmotionCategorizer
from cortex.server_intent_parser import parse_server_intent
from body.hardware_state_manager import HardwareStateManager
from body.indicators_manager import IndicatorsManager
from body.searchlight import Searchlight
from audio_input.audio_input_manager import AudioInputManager
from audio_input.audio_preprocessor import AudioPreprocessor
from audio_input.voice_recognition_manager import VoiceRecognitionManager
from audio_output.emotional_sounds_manager import EmotionalSoundsManager
from audio_output.response_manager import Response_Manager
from helpers.gateway_server_client import GatewayClient
from helpers.prompt_builder import PromptBuilder
from eyes.EyeConfig import EyeConfig
from eyes.EyeExpressionManager import EyeExpressionManager
from eyes.EyeFrameComposer import EyeFrameComposer
from eyes.EyeGazeInterpolator import GazeInterpolator

# Hardware items
hardware_state = HardwareStateManager()
searchlight = Searchlight()
indicators = IndicatorsManager(LED_INDICATOR)

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
emotion_categorizer = EmotionCategorizer()
response_manager = Response_Manager(picrawler_instance, actions_manager)
audio_input = AudioInputManager(picrawler_instance)
preprocessor = AudioPreprocessor()
voice_recognition = VoiceRecognitionManager()
unified_server = GatewayClient(server_host)
prompt_builder = PromptBuilder()
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

    indicators.start()
    indicators.set_mode("idle")

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

        indicators.set_mode("busy")

        recognized_speaker = voice_recognition.recognize_speaker(pcm_audio)

        # Hal will attempt to determine if the detected speech requires a response
        # call to stubbed voice analysis method will default boolean TRUE during testing
        if audio_input.respond_to_voice_input(pcm_audio, recognized_speaker):
            print("[Voice Analysis] Positive response. Proceeding with cognition loop.")

        if recognized_speaker != "Unknown":
            print(f"[Speaker Recognition] Identified speaker: {recognized_speaker}")
        else:
            print("[Speaker Recognition] Speaker is Unknown.")

        wav_bytes = preprocessor.pcm_to_16k_wav(pcm_audio)
        transcription = await unified_server.transcribe_audio(wav_bytes)
        # print(f"[Transcription RAW] {transcription}")

        spoken_text = transcription.get("text", "")
        speaker_emotion = emotion_categorizer.analyze_text_emotion(spoken_text)
        if not spoken_text:
            continue

        hardware_state.update()
        snapshot = perception.snapshot()
        perception.update(
            speaker_text=spoken_text,
            speaker_emotion=speaker_emotion,
            speaker=recognized_speaker,
            faces=snapshot["faces"],
            objects=snapshot["objects"],
            qr_codes=snapshot["qr_codes"],
            audio_direction=None,
            last_action=None,
            speech_confidence=transcription.get("confidence"),
            utterance_duration=transcription.get("duration"),
            truncated=truncated,
            hardware_status=hardware_state.snapshot(),
        )

        # SEND TO UNIFIED SERVER (COGNITION) -------------------------------
        prompt = prompt_builder.build_prompt(
            world_state.snapshot(),
            internal_state.snapshot(),
            perception.snapshot()
        )
        # DEBUG OUTPUT ------------------------------------------------------
        print("[Cognition] Sending prompt to server…")
        print("----- BEGIN PROMPT -----")
        print(prompt)
        print("------ END PROMPT ------")
        # END DEBUG OUTPUT --------------------------------------------------

        payload = {"prompt": prompt}

        server_json = await unified_server.send_perception(payload)



        try:
            server_json = await unified_server.send_perception(payload)
            server_intent = parse_server_intent(server_json)
            print(f"[Cognition] Server intent: {server_intent}")
        except Exception as e:
            print(f"[Server Error] {e}")
            server_intent = {"intent": "experience entropy"}

        # RESET PERCEPTION -------------------------------------------------
        perception.reset()

        # DECISION LAYER ---------------------------------------------------
        cortex.tick(server_intent)
        print(f"[Decision] Executed plan for intent '{server_intent.get('intent')}'")
        # LOOP --------------------------------------------------------------
        print("[Hal] Listening.")
        indicators.set_mode("idle")
        await asyncio.sleep(0.01)


async def graceful_shutdown():

    print("[Shutdown] Resetting MCU...")

    indicators.set_mode("off")
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
