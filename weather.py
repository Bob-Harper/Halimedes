import os
import requests
from collections import defaultdict
from dotenv import load_dotenv

# Load environment variables from a .env file
load_dotenv()

class WeatherHelper:
    def __init__(self):
        self.default_lat = os.getenv("DEFAULT_WEATHER_LAT")
        self.default_lon = os.getenv("DEFAULT_WEATHER_LONG")
        self.weather_api_key = os.getenv("OPEN_WEATHER")

    @staticmethod
    def get_wind_speed_description(speed):
        if speed < 1:
            return "Calm"
        elif speed < 5:
            return "Light breeze"
        elif speed < 11:
            return "Gentle breeze"
        elif speed < 19:
            return "Moderate wind"
        elif speed < 28:
            return "Fresh breeze"
        elif speed < 38:
            return "Strong wind"
        elif speed < 49:
            return "Gale"
        elif speed < 61:
            return "Strong gale"
        elif speed < 74:
            return "Storm"
        else:
            return "Hurricane-force winds"

    @staticmethod
    def get_wind_direction(degrees):
        cardinal_directions = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]
        index = round(degrees / 45) % 8
        return cardinal_directions[index]

    @staticmethod
    def get_cloud_description(cloud_percentage):
        if cloud_percentage <= 10:
            return "No clouds"
        elif cloud_percentage <= 25:
            return "Mostly clear"
        elif cloud_percentage <= 50:
            return "Partly cloudy"
        elif cloud_percentage <= 75:
            return "Mostly cloudy"
        else:
            return "Overcast"

    async def fetch_weather(self):
        """Fetch and format current weather data."""
        try:
            url = "http://api.openweathermap.org/data/2.5/weather"
            params = {
                "lat": self.default_lat,
                "lon": self.default_lon,
                "appid": self.weather_api_key,
                "units": "metric"
            }
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            # Format weather data
            location_name = data.get("name", "Unknown location")
            weather_desc = data["weather"][0]["description"].capitalize()
            temp = round(data["main"]["temp"])
            feels_like = round(data["main"]["feels_like"])
            clouds = self.get_cloud_description(data["clouds"]["all"])
            wind_speed = self.get_wind_speed_description(data["wind"]["speed"])
            wind_direction = self.get_wind_direction(data["wind"]["deg"])

            return (
                f"Weather in {location_name}: {weather_desc}. "
                f"Cloudiness: {clouds}. "
                f"Temperature: {temp}°C (feels like {feels_like}°C). "
                f"Wind: {wind_speed} from {wind_direction}."
            )

        except requests.RequestException as e:
            print(f"Weather API error: {e}")
            return "Sorry, I couldn't fetch the current weather."

    async def fetch_forecast(self):
        """Fetch and format a detailed 5-day forecast."""
        try:
            url = "http://api.openweathermap.org/data/2.5/forecast"
            params = {
                "lat": self.default_lat,
                "lon": self.default_lon,
                "appid": self.weather_api_key,
                "units": "metric"
            }
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            # Group data by day
            forecast_list = data["list"]
            daily_data = defaultdict(list)

            for entry in forecast_list:
                date = entry["dt_txt"].split(" ")[0]  # Extract the date
                daily_data[date].append(entry)

            # Summarize each day (process all available days, no artificial limits)
            all_days_summary = []
            for date, entries in daily_data.items():
                temps = [entry["main"]["temp"] for entry in entries]
                descriptions = [entry["weather"][0]["description"].capitalize() for entry in entries]
                high_temp = max(temps)
                low_temp = min(temps)
                common_weather = max(set(descriptions), key=descriptions.count)

                all_days_summary.append({
                    "date": date,
                    "high_temp": round(high_temp),
                    "low_temp": round(low_temp),
                    "description": common_weather,
                })

            return all_days_summary

        except requests.RequestException as e:
            print(f"Forecast API error: {e}")
            return None
