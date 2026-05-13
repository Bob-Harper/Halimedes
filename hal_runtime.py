# hal_runtime.py

import os
import warnings
import asyncio
from aiohttp import web

from crawler_utils.utils import reset_mcu
from runtime.loaders import HotSwapLoader

from body.picrawler import Picrawler
from body.picrawler_extended import PicrawlerExtended
from body.unified_motors import UnifiedMotors
from body.hardware_state_manager import HardwareStateManager
from body.sensor_state_manager import SensorStateManager
from body.searchlight import Searchlight
from body.indicators_manager import IndicatorsManager
from kernel.reflexes import load_all_reflexes
from eyes.EyeConfig import EyeConfig
from eyes.EyeFrameComposer import EyeFrameComposer
from eyes.EyeGazeInterpolator import GazeInterpolator
from eyes.EyeExpressionManager import EyeExpressionManager
from eyes.eye_channels import GazeChannel, ExpressionChannel

from audio_input.audio_preprocessor import AudioPreprocessor
from audio_input.audio_input_manager import AudioInputManager
from audio_input.voice_recognition_manager import VoiceRecognitionManager
from audio_output.emotional_sounds_manager import EmotionalSoundsManager
from audio_output.response_manager import Response_Manager

from vision_processing.vision_manager import VisionManager

from cortex.server_intent_parser import parse_server_intent

from helpers.api_server import create_hal_api
from helpers.global_config import LED_INDICATOR, UNIFIED_API_GATEWAY

from activeloop import ActiveLoop

warnings.simplefilter("ignore")


class Hal:
    def __init__(self, debug_reasoning: bool = False):
        # --- env reset (preserve existing behavior) ---
        os.environ.clear()

        self.DEBUG_REASONING = debug_reasoning
        self.server_host = UNIFIED_API_GATEWAY

        # --- core helpers ---
        self.hotswap = HotSwapLoader()  # DANGER ZONE: DO NOT HOTSWAP ENABLE HARDWARE.  ONLY ENABLE PURE SOFTWARE SYSTEMS.

        # --- body / hardware ---
        self.picrawler_instance = Picrawler()
        self.picrawler_extended = PicrawlerExtended(self.picrawler_instance)
        self.motors = UnifiedMotors(self.picrawler_instance, self.picrawler_extended)
        self.actions_manager = self.picrawler_instance
        self.hardware_state = HardwareStateManager()
        self.sensor_state = SensorStateManager()
        self.searchlight = Searchlight()
        self.indicators = IndicatorsManager(LED_INDICATOR)
        self.reflexes = load_all_reflexes()

        # --- eyes ---
        eye_profile = EyeConfig.load_eye_profile("whitegold01")
        self.composer = EyeFrameComposer(eye_profile)
        self.gaze_interpolator = GazeInterpolator()
        self.expression_manager = EyeExpressionManager()
        self.composer.setup(self.gaze_interpolator, self.expression_manager)
        self.gaze_interpolator.setup(self.composer)
        self.expression_manager.setup(self.composer)
        self.gaze_channel = GazeChannel(self.gaze_interpolator)
        self.expression_channel = ExpressionChannel(self.expression_manager)

        # --- audio ---
        self.preprocessor = AudioPreprocessor()
        self.audio_input = AudioInputManager(self.picrawler_instance)
        self.voice_recognition = VoiceRecognitionManager()
        self.emotion_sound_manager = EmotionalSoundsManager()
        self.response_manager = Response_Manager(self.picrawler_instance, self.actions_manager)

        # --- vision ---
        self.vision = VisionManager()

        # --- cortex (hotswapped) ---  # HOTSWAP SAFETY ZONE: CORTEX, HELPERS, AND ACTIVELOOP ONLY.  NEVER HOTSWAP ANYTHING THAT EVEN KNOWS HARDWARE EXISTS.
        self.internal_state = self.hotswap.load_module("cortex.internal_state_manager", "InternalStateManager")()
        self.world_state = self.hotswap.load_module("cortex.world_state_manager", "WorldStateManager")()
        self.initiative_manager = self.hotswap.load_module("cortex.initiative_manager", "InitiativeManager")()
        self.emotion_categorizer = self.hotswap.load_module("cortex.emotions_manager", "EmotionCategorizer")()
        self.semantic = self.hotswap.load_module("cortex.semantic_memory", "SemanticMemory")(self.server_host)
        self.episodic = self.hotswap.load_module("cortex.episodic_memory", "EpisodicMemory")(self.server_host)
        self.embedder = self.hotswap.load_module("cortex.embedding", "Embedder")()
        self.context_builder = self.hotswap.load_module("cortex.context_builder", "ContextBuilder")()
        self.perception = self.hotswap.load_module("cortex.perception_manager", "PerceptionManager")(
            hardware_state=self.hardware_state,
            sensor_state=self.sensor_state,
            emotion_categorizer=self.emotion_categorizer,
            vision=self.vision
        )
        self.decision_manager = self.hotswap.load_module("cortex.decision_manager", "DecisionManager")()
        self.decision_manager.attach_memory(self.embedder, self.semantic, self.episodic)
        self.action_executor = self.hotswap.load_module("cortex.action_executor", "ActionExecutor")(
            motors=self.motors,
            searchlight=self.searchlight,
            audio=self.response_manager,
            gaze_channel=self.gaze_channel,
            expression_channel=self.expression_channel,
        )
        self.behavior_executor = self.hotswap.load_module("cortex.behavior_executor", "BehaviorExecutor")(self.action_executor, self.response_manager)
        self.cortex = self.hotswap.load_module("cortex.cognitive_relay", "CognitiveRelay")(
            perception_manager=self.perception,
            context_builder=self.context_builder,
            initiative_manager=self.initiative_manager,
            decision_manager=self.decision_manager,
            behavior_executor=self.behavior_executor,
            internal_state_manager=self.internal_state,   # ← PASS IT IN
        )


        # --- helpers (hotswapped) ---
        self.unified_server = self.hotswap.load_module("helpers.gateway_server_client", "GatewayClient"
        )(self.server_host)
        self.event_builder = self.hotswap.load_module("helpers.event_builder", "EventBuilder")


        # --- API server holder ---
        self._api_runner = None

        # --- ActiveLoop with a controlled "globals" dict ---
        self.loop = ActiveLoop(self.hotswap, self._build_globals_dict())

    def _build_globals_dict(self):
        # This mirrors your old globals() usage, but under Hal’s control.
        return {
            "DEBUG_REASONING": self.DEBUG_REASONING,
            "hardware_state": self.hardware_state,
            "searchlight": self.searchlight,
            "indicators": self.indicators,
            "composer": self.composer,
            "gaze_interpolator": self.gaze_interpolator,
            "expression_manager": self.expression_manager,
            "preprocessor": self.preprocessor,
            "audio_input": self.audio_input,
            "voice_recognition": self.voice_recognition,
            "emotion_sound_manager": self.emotion_sound_manager,
            "response_manager": self.response_manager,
            "vision": self.vision,
            "internal_state": self.internal_state,
            "world_state": self.world_state,
            "initiative_manager": self.initiative_manager,
            "emotion_categorizer": self.emotion_categorizer,
            "semantic": self.semantic,
            "episodic": self.episodic,
            "embedder": self.embedder,
            "context_builder": self.context_builder,
            "perception": self.perception,
            "decision_manager": self.decision_manager,
            "action_executor": self.action_executor,
            "cortex": self.cortex,
            "unified_server": self.unified_server,
            "event_builder": self.event_builder,
            "parse_server_intent": parse_server_intent,
        }

    async def start_api(self):
        api_app = create_hal_api(self.hardware_state)
        self._api_runner = web.AppRunner(api_app)
        await self._api_runner.setup()
        site = web.TCPSite(self._api_runner, "0.0.0.0", 8123)
        await site.start()

    async def run(self):
        print("[Hal] Entering main loop.")

        await self.hardware_state.start()
        await self.sensor_state.start()
        await self.start_api()

        self.indicators.start()
        self.indicators.set_mode("idle")

        # Start eye rendering loop
        asyncio.create_task(self.composer.start_loop())

        await self.loop.run()

    async def shutdown(self):
        print("[Shutdown] Resetting MCU...")

        self.indicators.set_mode("off")
        reset_mcu()

        # If you later need to stop hardware_state or API runner, do it here.
        # e.g.:
        # if self._api_runner is not None:
        #     await self._api_runner.cleanup()

        print("[Shutdown] Done.")
