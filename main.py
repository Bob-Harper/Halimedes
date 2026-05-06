# Debug
DEBUG_REASONING = False
from crawler_utils.utils import reset_mcu
import warnings
warnings.simplefilter('ignore')

# Basic Imports
from aiohttp import web
import asyncio
import os
import json

# Explicitly clear any previously cached env variables
os.environ.clear()

"""
NOTE Import the Picrawler class first to pass through.
This prevents multiple initializations of the Picrawler class.
Multiple implementation is NOT harmless, it is 100% disruptive.
"""
from body.picrawler import Picrawler
picrawler_instance = Picrawler()
actions_manager = picrawler_instance

# Hot Swap Import Setup
from runtime.loaders import HotSwapLoader
hotswap = HotSwapLoader()

# Hardware Imports
from body.hardware_state_manager import HardwareStateManager
from body.searchlight import Searchlight
from body.indicators_manager import IndicatorsManager

# Eyes Imports
from eyes.EyeConfig import EyeConfig
from eyes.EyeFrameComposer import EyeFrameComposer
from eyes.EyeGazeInterpolator import GazeInterpolator
from eyes.EyeExpressionManager import EyeExpressionManager

# Audio Imports
from audio_input.audio_preprocessor import AudioPreprocessor
from audio_input.audio_input_manager import AudioInputManager
from audio_input.voice_recognition_manager import VoiceRecognitionManager
from audio_output.emotional_sounds_manager import EmotionalSoundsManager
from audio_output.response_manager import Response_Manager

#Visual Imports
from vision_processing.vision_manager import VisionManager

# Cortex Imports
from cortex.server_intent_parser import parse_server_intent

# Helpers Imports
from helpers.api_server import create_hal_api
from helpers.global_config import LED_INDICATOR
from helpers.global_config import UNIFIED_API_GATEWAY
server_host = UNIFIED_API_GATEWAY

# Import Active Loop
from activeloop import ActiveLoop
# Hardware Initialization
hardware_state = HardwareStateManager()
searchlight = Searchlight()
indicators = IndicatorsManager(LED_INDICATOR)

# Eyes Initialization
eye_profile = EyeConfig.load_eye_profile("whitegold01")
composer = EyeFrameComposer(eye_profile)
gaze_interpolator = GazeInterpolator()
expression_manager = EyeExpressionManager()
composer.setup(gaze_interpolator, expression_manager)

# Audio Initialization
preprocessor = AudioPreprocessor()
audio_input = AudioInputManager(picrawler_instance)
voice_recognition = VoiceRecognitionManager()
emotion_sound_manager = EmotionalSoundsManager()
response_manager = Response_Manager(picrawler_instance, actions_manager)

#Visual Initialization
vision = VisionManager()

# Cortex Initialization
internal_state = hotswap.load_module("cortex.internal_state_manager", "InternalStateManager")
world_state = hotswap.load_module("cortex.world_state_manager", "WorldStateManager")
initiative_manager = hotswap.load_module("cortex.initiative_manager", "InitiativeManager")
emotion_categorizer = hotswap.load_module("cortex.emotions_manager", "EmotionCategorizer")
semantic = hotswap.load_module("cortex.semantic_memory", "SemanticMemory")(server_host)
episodic = hotswap.load_module("cortex.episodic_memory", "EpisodicMemory")(server_host)
embedder = hotswap.load_module("cortex.embedding", "Embedder")
context_builder = hotswap.load_module("cortex.context_builder", "ContextBuilder")
perception = hotswap.load_module("cortex.perception_manager", "PerceptionManager")(hardware_state, emotion_categorizer, vision)
decision_manager = hotswap.load_module("cortex.decision_manager", "DecisionManager")()
decision_manager.attach_memory(embedder, semantic, episodic)
action_executor = hotswap.load_module("cortex.action_executor", "ActionExecutor")(
    motors=actions_manager,
    eyes=expression_manager,
    searchlight=searchlight,
    audio=response_manager
)
cortex = hotswap.load_module("cortex.cognition_loop", "CognitionLoop")(
    perception_manager=perception,
    context_builder=context_builder,
    initiative_manager=initiative_manager,
    decision_manager=decision_manager,
    action_executor=action_executor,
)

# Helpers Initialization
unified_server = hotswap.load_module("helpers.gateway_server_client", "GatewayClient")(server_host)
prompt_builder = hotswap.load_module("helpers.prompt_builder", "PromptBuilder")
event_builder = hotswap.load_module("helpers.event_builder", "EventBuilder")


async def main():
    print("[Hal] Entering main loop.")

    await hardware_state.start()

    api_app = create_hal_api(hardware_state)
    runner = web.AppRunner(api_app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", 8123)
    await site.start()

    indicators.start()
    indicators.set_mode("idle")

    loop = ActiveLoop(hotswap, globals())

    print("[Hal] Listening.")
    await loop.run()


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
