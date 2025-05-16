import os
from pathlib import Path
from dotenv import load_dotenv
from gpiozero import LED


def getenv_required(key: str) -> str:
    value = os.getenv(key)
    if value is None:
        raise EnvironmentError(f"Missing required environment variable: {key}")
    return value


def getenv_optional(key: str, default: str = "") -> str:
    value = os.getenv(key)
    if value is None:
        return default
    return value


# Load .env once at startup
load_dotenv()

# Store environment variables as global constants
OPEN_WEATHER_1DAY = getenv_required("OPEN_WEATHER_1DAY")
OPEN_WEATHER_5DAY = getenv_required("OPEN_WEATHER_5DAY")
OPEN_WEATHER = getenv_required("OPEN_WEATHER")
DEFAULT_WEATHER_LAT = getenv_optional("DEFAULT_WEATHER_LAT")
DEFAULT_WEATHER_LONG = getenv_optional("DEFAULT_WEATHER_LONG")
OLLAMASTYGIA = getenv_optional("OLLAMASTYGIA")
OLLAMALAPTOP = getenv_required("OLLAMALAPTOP")
NEWSAPIDOTORG = getenv_required("NEWSAPIDOTORG")
NEWSAPIDOTCOM = getenv_optional("NEWSAPIDOTCOM")

# GPIO pins for hardware
# Define but don't initialize
LED_INDICATOR = LED(26)

# Paths are now kept in .env so we dont need to hardcode 

# DualEye Display 
EYE_ASSETS_PATH = Path(getenv_required("EYE_ASSETS_PATH"))
EYE_CACHE_PATH = Path(getenv_required("EYE_CACHE_PATH"))
EYE_EXPRESSIONS_PATH = Path(getenv_required("EYE_EXPRESSIONS_PATH"))
EYE_EXPRESSIONS_FILE = Path(getenv_required("EYE_EXPRESSIONS_FILE"))

# Sound Files
SOUND_ASSETS_PATH = Path(getenv_required("SOUND_ASSETS_PATH"))

# Core SPEECH model 
SPEECH_MODEL_PATH = Path(getenv_required("SPEECH_MODEL_PATH"))
SPEECH_MODEL_NAME = getenv_required("SPEECH_MODEL_NAME")

# Voice recognition config 
VOICE_RECOGNITION_MODEL_PATH = Path(getenv_required("VOICE_RECOGNITION_MODEL_PATH"))
VOICE_RECOGNITION_MODEL_NAME = getenv_required("VOICE_RECOGNITION_MODEL_NAME")
VOICEPRINT_MODEL_DIR = Path(getenv_required("VOICEPRINT_MODEL_DIR"))

# These will be moved to DB after testing phase
VOICEPRINT_USER1_NAME = getenv_required("VOICEPRINT_USER1_NAME")
VOICEPRINT_USER1_MODEL = getenv_required("VOICEPRINT_USER1_MODEL")
VOICEPRINT_USER2_NAME = getenv_optional("VOICEPRINT_USER2_NAME")
VOICEPRINT_USER2_MODEL = getenv_optional("VOICEPRINT_USER2_MODEL")