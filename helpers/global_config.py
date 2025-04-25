import os
from pathlib import Path
from dotenv import load_dotenv
from gpiozero import LED, Button

# Load .env once at startup
load_dotenv()

# Store environment variables as global constants
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
OPEN_WEATHER_1DAY = os.getenv("OPEN_WEATHER_1DAY")
OPEN_WEATHER_5DAY = os.getenv("OPEN_WEATHER_5DAY")
OPEN_WEATHER = os.getenv("OPEN_WEATHER")
DEFAULT_WEATHER_LAT = os.getenv("DEFAULT_WEATHER_LAT")
DEFAULT_WEATHER_LONG = os.getenv("DEFAULT_WEATHER_LONG")
OLLAMASTYGIA = os.getenv("OLLAMASTYGIA")
OLLAMALAPTOP = os.getenv("OLLAMALAPTOP")
HUGGY_TOKEN = os.getenv("HUGGY_TOKEN")
NEWSAPIDOTORG = os.getenv("NEWSAPIDOTORG")
NEWSAPIDOTCOM = os.getenv("NEWSAPIDOTCOM")

# GPIO pins for hardware
# Define but don't initialize
LED_INDICATOR = LED(26)

# Paths are now kept in .env so we dont need to hardcode and take 
# forever fixing after a refactor because vscode is a bitch
EYE_ASSETS_PATH = Path(os.getenv("EYE_ASSETS_PATH"))
SOUND_ASSETS_PATH = Path(os.getenv("SOUND_ASSETS_PATH"))
EYE_CACHE_PATH = Path(os.getenv("EYE_CACHE_PATH"))