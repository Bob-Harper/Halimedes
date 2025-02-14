import os
from dotenv import load_dotenv

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