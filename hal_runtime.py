# hal_runtime.py
# OGO:  refers to Out Of Grouped Order.  Keeping all linked modules together is not always possible.  Do not move these without careful consideration.
print("[Startup] Importing System Modules.")
import os
import warnings
import asyncio
from aiohttp import web
from crawler.utils import reset_mcu # OGO: to reset mcu in case of prior crash and lockup
from runtime.loaders import HotSwapLoader # Allows non hardware modules to be updated without needing to restart the main process.
from cortex.perception_manager import PerceptionManager # OGO: In cortex module but talks directly to hardware_manager and cannot be hotswapped
print("[Startup] Importing Hardware Modules.") # Servos, indicators, and other hardware not otherwise grouped together by function
from crawler.picrawler import Picrawler
from crawler.picrawler_extended import PicrawlerExtended
from crawler.searchlight import Searchlight
from body.posture_manager import PostureManager
from body.hardware_state_manager import HardwareStateManager
from body.indicators_manager import IndicatorsManager
print("[Startup] Importing Helper Modules.")
from helpers.api_server import create_hal_api
from helpers.global_config import LED_INDICATOR, UNIFIED_API_GATEWAY
print("[Startup] Importing Eye Display Modules.") # Eyes refer to LCD module, not vision processing
from eyes.EyeConfig import EyeConfig
from eyes.EyeFrameComposer import EyeFrameComposer
from eyes.EyeGazeInterpolator import GazeInterpolator
from eyes.EyeExpressionManager import EyeExpressionManager
from eyes.eye_channels import GazeChannel, ExpressionChannel
print("[Startup] Importing Audio Modules.") # Audio modules for handling audio input and output
from audio_input.audio_preprocessor import AudioPreprocessor
from audio_input.audio_input_manager import AudioInputManager
from audio_input.voice_recognition_manager import VoiceRecognitionManager
from audio_output.emotional_sounds_manager import EmotionalSoundsManager
from audio_output.response_manager import Response_Manager
print("[Startup] Importing Vision Modules.") # Camera and Vision processing modules and tools.
from vision_processing.vision_manager import VisionManager
print("[Startup] Importing Reflex Modules.")
from crawler.ultrasonic import UltrasonicDriver # OGO: In crawer module but is a sensor used for reflexes
from reflex.bno08x.i2c import IMUDriver
imu = IMUDriver(i2c_bus=1, address=0x4B)  # OGO:hardware driver Needs to be initialized before configureing IMU or loading Sensor State Manaager
from reflex.bno08x.enable_imu_reports import configure_imu
configure_imu(imu)  # Initialize IMU reports
from reflex.reflexes import load_all_reflexes
from reflex.reflexive_layer import ReflexEngine
from body.sensor_state_manager import SensorStateManager # OGO: In body module but is grouped with sensors at this is what manages them.  Loads last to give IMU time to init.

from activeloop import ActiveLoop # Main loop call that starts and maintains treads for individual processing loops.

warnings.simplefilter("ignore")
import faulthandler
faulthandler.enable()

class Hal:
    def __init__(self, debug_reasoning: bool = False):
        # --- env reset (preserve existing behavior) ---
        print("[Startup] Clearing previous environment variables.")
        os.environ.clear()

        self.DEBUG_REASONING = debug_reasoning
        self.server_host = UNIFIED_API_GATEWAY
        print("[Startup] Initializing System Modules.")
        # --- core helpers ---
        self.hotswap = HotSwapLoader()  # DANGER ZONE: DO NOT HOTSWAP ENABLE HARDWARE.  ONLY ENABLE PURE SOFTWARE SYSTEMS.  Do NOT enable PerceptionManager as it DOES directly affect hardware_state.
        print("[Startup] Initializing Hardware.")
        # --- body / hardware ---
        self.picrawler_instance = Picrawler() # ALWAYS init picrawler before any other hardware to pass instance to every module that uses it.  Allowing any module to create it's own instance will result in hardware conflicts.
        self.picrawler_extended = PicrawlerExtended(self.picrawler_instance)
        self.posture = PostureManager(self.picrawler_instance, self.picrawler_extended)
        self.actions_manager = self.picrawler_instance
        self.hardware_state = HardwareStateManager()
        self.imu = imu  # Store the IMU instance in the Hal class
        self.ultrasonic_driver = UltrasonicDriver()
        self.sensor_state = SensorStateManager(imu_driver=self.imu,ultrasonic_driver=self.ultrasonic_driver)
        self.searchlight = Searchlight()
        self.indicators = IndicatorsManager(LED_INDICATOR)
        self.reflexes = load_all_reflexes()
        self.reflex_engine = ReflexEngine(self.reflexes)
        # --- cortex / memory ---
        print("[Startup] Initializing Cognitive Memory.")
        self.semantic = self.hotswap.load_module("cortex.semantic_memory", "SemanticMemory")(self.server_host)
        self.episodic = self.hotswap.load_module("cortex.episodic_memory", "EpisodicMemory")(self.server_host)
        self.working_memory = self.hotswap.load_module("cortex.working_memory", "WorkingMemory")()
        self.embedder = self.hotswap.load_module("cortex.embedding", "Embedder")()
        print("[Startup] Initializing Eye Display.")
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

        print("[Startup] Initializing Vision.")
        self.vision = VisionManager()

        print("[Startup] Initializing Audio Output.")
        self.preprocessor = AudioPreprocessor()
        self.audio_input = AudioInputManager(self.picrawler_instance)
        self.voice_recognition = VoiceRecognitionManager()
        self.emotion_sound_manager = EmotionalSoundsManager()
        self.response_manager = Response_Manager(self.picrawler_instance, self.actions_manager, self.internal_state, working_memory=self.working_memory)

        # --- cortex (hotswapped) ---  # HOTSWAP SAFETY ZONE: CORTEX, HELPERS, AND ACTIVELOOP ONLY.  NEVER HOTSWAP ANYTHING THAT EVEN KNOWS HARDWARE EXISTS.
        print("[Startup] Initializing Cortex.")
        #
        self.perception = PerceptionManager( # OGO: only cortex module that talks directly to hardware and cannot be hotswapped
            hardware_state=self.hardware_state,
            sensor_state=self.sensor_state,
            emotion_categorizer=self.emotion_categorizer,
            vision=self.vision
        )
        self.internal_state = self.hotswap.load_module("cortex.internal_state_manager", "InternalStateManager")()
        self.world_state = self.hotswap.load_module("cortex.world_state_manager", "WorldStateManager")()
        self.initiative_manager = self.hotswap.load_module("cortex.initiative_manager", "InitiativeManager")()
        self.emotion_categorizer = self.hotswap.load_module("cortex.emotions_manager", "EmotionCategorizer")()
        self.context_builder = self.hotswap.load_module("cortex.context_builder", "ContextBuilder")(self.working_memory)
        self.behavior_manager = self.hotswap.load_module("cortex.behavior_manager", "BehaviorManager")()
        DecisionManagerClass = self.hotswap.load_module("cortex.decision_manager", "DecisionManager")
        self.decision_manager = DecisionManagerClass(
            internal_state_manager=self.internal_state,
            behavior_manager=self.behavior_manager
        )
        self.action_executor = self.hotswap.load_module("cortex.action_executor", "ActionExecutor")(
            internal_state=self.internal_state,
            posture=self.posture,
            searchlight=self.searchlight,
            audio=self.response_manager,
            gaze_channel=self.gaze_channel,
            expression_channel=self.expression_channel,
        )
        self.behavior_executor = self.hotswap.load_module("cortex.behavior_executor", "BehaviorExecutor")(self.action_executor, self.response_manager)
        CognitiveRelayClass = self.hotswap.load_module("cortex.cognitive_relay", "CognitiveRelay")
        self.cortex = CognitiveRelayClass(
            perception_manager=self.perception,
            context_builder=self.context_builder,
            initiative_manager=self.initiative_manager,
            decision_manager=self.decision_manager,
            behavior_manager=self.behavior_manager,   # ← ADD THIS
            behavior_executor=self.behavior_executor,
            internal_state_manager=self.internal_state,
        )

        print("[Startup] Initializing Helper Modules.")
        self.unified_server = self.hotswap.load_module("helpers.gateway_server_client", "GatewayClient"
        )(self.server_host)
        self.event_builder = self.hotswap.load_module("helpers.event_builder", "EventBuilder")()

        # --- API server holder ---
        print("[Startup] Initializing API Server.")
        self._api_runner = None

        # --- ActiveLoop with a controlled "globals" dict ---
        self.loop = ActiveLoop(self.hotswap, self._build_globals_dict())

    def _build_globals_dict(self):
        # Now everyone can access the HAL's components via the ActiveLoop's globals dictionary.
        print("[Startup] Building globals dictionary.")

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
            "working_memory": self.working_memory,
            "embedder": self.embedder,
            "context_builder": self.context_builder,
            "perception": self.perception,
            "decision_manager": self.decision_manager,
            "action_executor": self.action_executor,
            "cortex": self.cortex,
            "unified_server": self.unified_server,
            "event_builder": self.event_builder,
            "reflex_engine": self.reflex_engine,
            "reflexes": self.reflexes,
            "sensor_state": self.sensor_state,
            # direct drivers (legacy, optional) until we have sensor state manager fully integrated
            "imu": self.imu,
            "ultrasonic": self.ultrasonic_driver,
        }

    async def start_api(self):
        api_app = create_hal_api(self.hardware_state)
        self._api_runner = web.AppRunner(api_app)
        await self._api_runner.setup()
        site = web.TCPSite(self._api_runner, "0.0.0.0", 8123)
        await site.start()

    async def run(self):
        print("[Startup] Entering main loop.")

        await self.hardware_state.start()
        await self.sensor_state.start()
        await self.start_api()

        self.indicators.start()
        self.indicators.set_mode("idle")

        # Start eye rendering loop
        print("[Startup] Begin Eye Rendering.")

        asyncio.create_task(self.composer.start_loop())

        await self.loop.run()

    async def shutdown(self):
        print("[Shutdown] Resetting MCU...")

        self.indicators.set_mode("off")
        reset_mcu()

        # If we later need to stop hardware_state or API runner, do it here.
        # e.g.:
        # if self._api_runner is not None:
        #     await self._api_runner.cleanup()

        print("[Shutdown] Done.")
