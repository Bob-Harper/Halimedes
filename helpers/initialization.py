# New module: helpers.initialization.py
from helpers.response_utils import Response_Manager
from helpers.listener_utils import AudioInput
from helpers.verbal_commands import CommandManager
from helpers.voice_recognition import VoiceprintManager
from helpers.general_utilities import announce_battery_status
from helpers.emotions import EmotionHandler, EmotionSoundManager
from helpers.llm_utils import LLMClient
from helpers.passive_actions import PassiveActionsManager

def initialize_system():
    llm_client = LLMClient(server_host='http://192.168.0.123:11434')
    voiceprint_manager = VoiceprintManager()
    command_manager = CommandManager(llm_client)
    response_manager = Response_Manager()
    audio_input = AudioInput()
    emotion_handler = EmotionHandler()
    emotion_sound_manager = EmotionSoundManager()
    actions_manager = PassiveActionsManager()

    return {
        "llm_client": llm_client,
        "voiceprint_manager": voiceprint_manager,
        "command_manager": command_manager,
        "response_manager": response_manager,
        "audio_input": audio_input,
        "emotion_handler": emotion_handler,
        "emotion_sound_manager": emotion_sound_manager,
        "actions_manager": actions_manager,
    }
