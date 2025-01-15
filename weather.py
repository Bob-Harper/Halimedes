from decisions.lunar_effects import LunarEffects
import requests


@commands.command(name='weather')
async def get_weather(self, ctx, *args):
    """Fetch and respond with weather information."""
    try:
        # Determine the location
        location = " ".join(args).strip()

        if location:
            # Use Geocoding API to fetch coordinates for the city
            coords = self.fetch_coordinates(location)
            if not coords:
                await ctx.send(f"Sorry, I couldn't find coordinates for '{location}'.")
                return
            lat, lon = coords
        else:
            # Default to Fort Erie
            lat, lon = self.default_lat, self.default_lon

        # Fetch weather data using lat/lon
        weather_data = self.fetch_weather(lat, lon)
        if not weather_data:
            await ctx.send("Sorry, I couldn't retrieve weather data.")
            return

        # Format weather data
        formatted_data = self.format_weather_data(weather_data)

        # Build context_data
        context_data = await extract_context_data(ctx=ctx, bot=self.bot)
        context_data["weather_data"] = formatted_data

        # Send weather data to the language model
        chat_response_cog = self.bot.get_cog("ChatResponseCog")
        if not chat_response_cog:
            await ctx.send("I can't process the weather response right now. Try again later.")
            return

        response = await chat_response_cog.send_response_async(
            context_data=context_data,
            response_type="Weather_Update",
            model_type="text",
        )

        # Send the final response to the Discord channel
        await ctx.send(response or "I couldn't generate a response. Try again later.")

    except Exception as e:
        logger.error(f"Error in !weather command: {e}")
        await ctx.send("Something went wrong while fetching the weather.")


def fetch_coordinates(self, location):
    """Fetch latitude and longitude for a city using Geocoding API."""
    try:
        url = "http://api.openweathermap.org/geo/1.0/direct"
        params = {
            "q": location,
            "appid": self.weather_api_key,
            "limit": 1  # Fetch the most relevant match
        }
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        if data:
            return data[0]["lat"], data[0]["lon"]
        return None
    except requests.RequestException as e:
        logger.error(f"Geocoding API error: {e}")
        return None


def fetch_weather(self, lat, lon):
    """Fetch weather data from OpenWeatherMap API using lat/lon."""
    try:
        url = "http://api.openweathermap.org/data/2.5/weather"
        params = {
            "lat": lat,
            "lon": lon,
            "appid": self.weather_api_key,
            "units": "metric"
        }
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        logger.error(f"Weather API error: {e}")
        return None


@staticmethod
def format_weather_data(data):
    """Extract and format relevant weather details from API response."""
    try:
        location_name = data.get("name", "Unknown location")
        weather_desc = data["weather"][0]["description"].capitalize()
        temp = data["main"]["temp"]
        feels_like = data["main"]["feels_like"]
        humidity = data["main"]["humidity"]
        wind_speed = data["wind"]["speed"]

        return (
            f"Weather in {location_name}: {weather_desc}. "
            f"Temperature: {temp}°C (feels like {feels_like}°C). "
            f"Humidity: {humidity}%. Wind speed: {wind_speed} m/s."
        )
    except (KeyError, TypeError) as e:
        logger.error(f"Error formatting weather data: {e}")
        return "Weather data is unavailable."
