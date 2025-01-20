from rapidfuzz import fuzz, process
import asyncio
from helpers.picrawler import Picrawler
from helpers.new_movements import NewMovements
from helpers.voice_utils import speak_with_flite
import os
from helpers.batterytest import announce_battery_status
from helpers.passive_actions import PassiveActionsManager
from helpers.sound_effects import PassiveSoundsManager
from helpers.weather import WeatherHelper

class CommandManager:
    def __init__(self, llm_client):
        self.llm_client = llm_client
        self.weather_helper = WeatherHelper()
        self.crawler = Picrawler()
        self.newmovements = NewMovements(self.crawler)
        self.passive_manager = PassiveActionsManager()
        self.passive_sound = PassiveSoundsManager()

    async def command_shutdown(self, spoken_text):
        """Shutdown the robot."""
        await speak_with_flite(f"Verbal Command Detected: {spoken_text}. Please stand by.")
        system_prompt = 'You are Halimeedees, a quirky alien robot exploring Earth. Do not use asterisks or actions. No more chat for you, It is time to shut down and rest now.  Goodnight.'
        response_text = await self.llm_client.send_message_async(system_prompt, spoken_text)
        await self.passive_manager.shutdown_speech_actions(response_text)        
        await asyncio.to_thread(os.system, "sudo shutdown -h now")
        return True  # Signal to break the loop
    
    async def command_exit_chat(self, spoken_text):
        """Exit chat mode but remain powered."""
        await speak_with_flite(f"Verbal Command Detected: {spoken_text}. Please stand by.")
        system_prompt = 'You are Halimeedees, a quirky alien robot exploring Earth. Do not use asterisks or actions. The time of the chatting is over, the time of doing something else has begun.  goodbye.'
        response_text = await self.llm_client.send_message_async(system_prompt, spoken_text)
        await self.passive_manager.shutdown_speech_actions(response_text)     
        return True  # Signal to break the loop

    async def command_help(self, spoken_text):
        """Provide verbal help."""
        await speak_with_flite(f"I heard you say {spoken_text}. To have me power down, say shut down. To end chat but leave me powered up, say end chat.  to check my battery say battery.  to hear me repeat these instructions, say help.")

    async def command_battery(self, spoken_text):
        """Provide verbal battery status check."""
        await speak_with_flite(f"I heard you say {spoken_text}. Acknowledged, I will check battery status now.")
        await announce_battery_status()

    async def command_get_weather(self, spoken_text):
        """Provide today's weather."""
        await speak_with_flite("You want to check the weather? Okay, I'll stick my head out the window and look around.")
        current_weather = await self.weather_helper.fetch_weather()
        
        if not current_weather:
            await speak_with_flite("Sorry, I couldn't retrieve the weather. Maybe I need a new antenna.")
            return
        
        stop_event = asyncio.Event()
        # Generate response with isolated system prompt and a proper user query
        system_prompt = (
            f"You are Halimeedees, a quirky four legged crawler robot of unknown origin. "
            f"Here is the weather data for today: {current_weather}. Deliver an amusing and informative update, blending curiosity and wit. "
            f"Be engaging, but don't overcomplicate things—keep it clear and fun!"
        )
        spoken_text = "Please tell me the current weather."  # Overwrite with clean input
        # Start handling passive actions while waiting for LLM response
        thinking_task = asyncio.create_task(self.passive_manager.handle_passive_actions(stop_event))
        # Fetch LLM response
        response_text = await self.llm_client.send_message_async(system_prompt, spoken_text)
        # Stop passive actions
        stop_event.set()
        await thinking_task  # Wait for passive task to finish
        # Play the intro sound right before delivering the weather report
        await self.passive_sound.play_weather_intro_sound()
        await speak_with_flite(response_text)

        # Add the system prompt, user query, and response to the conversation history
        self.llm_client.conversation_history.append({"role": "system", "content": system_prompt})
        self.llm_client.conversation_history.append({"role": "user", "content": spoken_text})
        self.llm_client.conversation_history.append({"role": "assistant", "content": response_text})

    async def command_get_forecast(self, spoken_text):
        """Provide a 5-day weather forecast."""
        await speak_with_flite("You think I can predict the weather? Oh Boy, I'll check my crystal ball. Just kidding, I'll use a satellite.")
        weather_forecast = await self.weather_helper.fetch_forecast()
        
        if not weather_forecast:
            await speak_with_flite("Sorry, I couldn't retrieve the forecast. No satellites available to hijack.")
            return
        
        # Generate response with isolated system prompt and a proper user query
        system_prompt = (
            f"You are Halimeedees, a quirky four legged crawler robot of unknown origin. "
            f"Here is the weather data for the next five days: {weather_forecast}. Craft a fun and engaging response that highlights trends, keeps it concise, and throws in a pinch of your unique robotic humor. "
            f"Avoid getting bogged down in numbers — focus on the big picture!"
        )
        stop_event = asyncio.Event()
        spoken_text = "Please tell me the 5-day weather forecast."  # Overwrite with clean input
        # Start handling passive actions while waiting for LLM response
        thinking_task = asyncio.create_task(self.passive_manager.handle_passive_actions(stop_event))
        # Fetch LLM response
        response_text = await self.llm_client.send_message_async(system_prompt, spoken_text)
        # Stop passive actions
        stop_event.set()
        await thinking_task  # Wait for passive task to finish
        # Play the intro sound right before delivering the weather report
        await self.passive_sound.play_weather_intro_sound()
        await speak_with_flite(response_text)

        # Add the system prompt, user query, and response to the conversation history
        self.llm_client.conversation_history.append({"role": "system", "content": system_prompt})
        self.llm_client.conversation_history.append({"role": "user", "content": spoken_text})
        self.llm_client.conversation_history.append({"role": "assistant", "content": response_text})



    def match_command(self, input_text):
        """
        Match the input text to a command in the command map using fuzzy logic.
        Returns the best match if above the threshold, otherwise None.
        """
        threshold = 70  # Minimum similarity score to accept
        matches = process.extract(input_text, self.command_map.keys(), scorer=fuzz.ratio)
        if matches and matches[0][1] >= threshold:
            return matches[0][0]  # Return the best matching command
        return None
 
    @property
    def command_map(self):
        return {
            "shutdown": self.command_shutdown,
            "quit": self.command_exit_chat,
            "help": self.command_help,
            "battery": self.command_battery,
            "weather": self.command_get_weather,
            "forecast": self.command_get_forecast,
        }
    
