from helpers.response_manager import Response_Manager
from helpers.weather_handler import WeatherHandler
import asyncio


class WeatherCommandManager:
    def __init__(self, llm_client, passive_manager, passive_sound, picrawler_instance):
        self.llm_client = llm_client
        self.picrawler_instance = picrawler_instance
        self.passive_manager = passive_manager
        self.passive_sound = passive_sound
        self.weather_helper = WeatherHandler()
        self.response_manager = Response_Manager(self.picrawler_instance)

    async def startup_fetch_forecast(self):
        # Fetch the 5-day weather forecast
        weather_forecast = await self.weather_helper.fetch_forecast()
        if not weather_forecast:
            await self.response_manager.speak_with_flite("Checking weather satellite connection. Status: Offline.")
            return
        await self.response_manager.speak_with_flite("Checking weather satellite connection. Status: Online.")
        # Add history for LLM
        self.llm_client.conversation_history.extend([
            {"role": "system", "content": f"If the conversation is weather related, here is the most recent 5-day forecast: {weather_forecast}."}
        ])
        
    async def command_get_weather(self, spoken_text):
        """Provide today's weather."""
        await self.response_manager.speak_with_flite("You want to check the weather? Okay, I'll stick my head out the window and look around.")

        # Fetch the current weather
        current_weather = await self.weather_helper.fetch_weather()
        if not current_weather:
            await self.response_manager.speak_with_flite("Sorry, I couldn't retrieve the weather. Maybe I need a new antenna.")
            return

        # Start passive actions
        stop_event = asyncio.Event()
        thinking_task = asyncio.create_task(self.passive_manager.handle_passive_actions(stop_event))

        # Generate LLM system prompt and response
        system_prompt = (
            f"You are Halimeedees, a quirky four-legged crawler robot. "
            f"Here is the weather data for today: {current_weather}. "
            f"Deliver an amusing and informative update, blending curiosity and wit. "
        )
        response_text = await self.llm_client.send_message_async(system_prompt, spoken_text)
        # Ensure passive actions are stopped
        stop_event.set()
        await thinking_task  # Wait for passive actions to stop
        # Play the weather intro sound
        await self.passive_sound.play_weather_intro_sound()
        # Speak the response
        await self.response_manager.speak_with_flite(response_text)

        # Add history for LLM
        self.llm_client.conversation_history.extend([
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": spoken_text},
            {"role": "assistant", "content": response_text},
        ])
        return False  # Signal to go back to listening

    async def command_get_forecast(self, spoken_text):
        """Provide a 5-day weather forecast."""
        await self.response_manager.speak_with_flite("You think I can predict the weather? Oh Boy, I'll check my crystal ball. Just kidding, I'll use a satellite.")

        # Fetch the 5-day weather forecast
        weather_forecast = await self.weather_helper.fetch_forecast()
        if not weather_forecast:
            await self.response_manager.speak_with_flite("Sorry, I couldn't retrieve the forecast. No satellites available to hijack.")
            return

        # Start passive actions
        stop_event = asyncio.Event()
        thinking_task = asyncio.create_task(self.passive_manager.handle_passive_actions(stop_event))

        # Generate LLM system prompt and response
        system_prompt = (
            f"You are Halimeedees, a quirky four-legged crawler robot of unknown origin. "
            f"Here is the weather data for the next five days: {weather_forecast}. "
            f"Craft a fun and engaging response that highlights trends, keeps it concise but interesting. "
            f"Numbers are okay but focus on the big picture!"
        )
        response_text = await self.llm_client.send_message_async(system_prompt, spoken_text)
        # Ensure passive actions are stopped
        stop_event.set()
        await thinking_task  # Wait for passive actions to stop
        # Play the weather intro sound
        await self.passive_sound.play_weather_intro_sound()
        # Speak the response
        await self.response_manager.speak_with_flite(response_text)
        # Add history for LLM
        self.llm_client.conversation_history.extend([
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": spoken_text},
            {"role": "assistant", "content": response_text},
        ])
        return False  # Signal to go back to listening
