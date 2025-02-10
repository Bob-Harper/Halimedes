from rapidfuzz import fuzz
import asyncio
from helpers.picrawler import Picrawler
from helpers.new_movements import NewMovements
import subprocess
from helpers.general_utilities import GeneralUtilities
from helpers.passive_actions import PassiveActionsManager
from helpers.passive_sounds import PassiveSoundsManager
from helpers.response_utils import Response_Manager
from helpers.weather import WeatherHelper
from helpers.weather_commands import WeatherCommandManager
from helpers.news_api import fetch_top_news
import signal
import sys


# Shutdown signal handler
def handle_shutdown_signal(signal_number, frame):
    print("Shutdown signal received. Exiting gracefully...")
    sys.exit(0)


# Attach the signal handler to system termination signals
signal.signal(signal.SIGTERM, handle_shutdown_signal)
signal.signal(signal.SIGINT, handle_shutdown_signal)


class CommandManager:
    def __init__(self, llm_client):
        self.llm_client = llm_client
        self.weather_helper = WeatherHelper()
        self.crawler = Picrawler()
        self.newmovements = NewMovements(self.crawler)
        self.passive_manager = PassiveActionsManager()
        self.passive_sound = PassiveSoundsManager()
        self.weather_commands = WeatherCommandManager(llm_client, self.passive_manager, self.passive_sound)
        self.response_manager = Response_Manager()
        self.general_utils = GeneralUtilities()

    async def handle_command(self, spoken_text):
        command = self.match_command(spoken_text)  # Check if input matches a known command
        if command:
            should_exit = await self.command_map[command]["function"](spoken_text)
            return True, should_exit  # Return that a command was detected, and whether to exit
        return False, False  # No command detected, don't exit

    # Command names mapped to their associated function and conversational phrases
    @property
    def command_map(self):
        return {
            "shutdown": {
                "function": self.command_shutdown,
                "phrases": ["shutdown", "power off", "turn off"],
            },
            "quit": {
                "function": self.command_exit_chat,
                "phrases": ["quit", "exit chat", "we’re done", "stop talking"],
            },
            "help": {
                "function": self.command_help,
                "phrases": ["help", "what can you do", "commands"],
            },
            "battery": {
                "function": self.command_battery,
                "phrases": ["battery", "check battery status", "power level"],
            },
            "weather": {
                "function": self.weather_commands.command_get_weather,
                "phrases": ["weather", "current weather", "what's the weather"],
            },
            "forecast": {
                "function": self.weather_commands.command_get_forecast,
                "phrases": ["forecast", "what's the forecast", "weather tomorrow", "what’s tomorrow’s weather"],
            },
            "news": {
                "function": self.command_get_news,
                "phrases": ["news", "check the news", "tell me the news", "what's new today"]
            },
        }
    
    def match_command(self, input_text):
        """
        Match the input text to a command using fuzzy logic and conversational mappings.
        Returns the command name if matched, otherwise None.
        """
        threshold = 70  # Minimum similarity score to accept
        best_match = None
        best_score = 0

        # Loop through commands and match against associated phrases
        for command_name, command_data in self.command_map.items():
            for phrase in command_data["phrases"]:
                match_score = fuzz.ratio(input_text.lower(), phrase.lower())
                if match_score > best_score and match_score >= threshold:
                    best_score = match_score
                    best_match = command_name

        if best_match:
            return best_match  # Return the matched command name
        return None
    
    async def command_shutdown(self, spoken_text):
        """Shutdown the robot."""
        await self.response_manager.speak_with_flite(f"Verbal Command Detected: {spoken_text}. Please stand by.")
        system_prompt = 'You are Halimeedees, a quirky alien robot exploring Earth. Do not use asterisks or actions. No more chat for you, It is time to shut down and rest now.  Goodnight.'
        response_text = await self.llm_client.send_message_async(system_prompt, spoken_text)
        # Small delay to ensure the message is heard before the shutdown
        await asyncio.sleep(1)
        await self.passive_manager.shutdown_speech_actions(response_text)        
        await asyncio.to_thread(subprocess.run, ["sudo", "shutdown", "-h", "now"])        
        return True  # Signal to break the loop
    
    async def command_exit_chat(self, spoken_text):
        """Exit chat mode but remain powered."""
        await self.response_manager.speak_with_flite(f"Verbal Command Detected: {spoken_text}. Please stand by.")
        system_prompt = 'You are Halimeedees, a quirky alien robot exploring Earth. Do not use asterisks or actions. The time of the chatting is over, the time of doing something else has begun. Goodbye.'
        response_text = await self.llm_client.send_message_async(system_prompt, spoken_text)
        
        # Wait for shutdown actions to complete
        await self.passive_manager.shutdown_speech_actions(response_text)  
        
        # Add a delay to ensure the action visibly completes
        await asyncio.sleep(1)  
        return True  # Signal to break the loop

    async def command_help(self, spoken_text):
        """Provide verbal help."""
        await self.response_manager.speak_with_flite(f"I heard you say {spoken_text}. To have me power down, say shut down. To end chat but leave me powered up, say end chat.  to check my battery say battery.  to hear me repeat these instructions, say help.")
        return False  # Signal to go back to listening
    
    async def command_battery(self, spoken_text):
        """Provide verbal battery status check."""
        await self.response_manager.speak_with_flite(f"I heard you say {spoken_text}. Acknowledged, I will check battery status now.")
        await self.general_utils.announce_battery_status()
        return False  # Signal to go back to listening

    async def command_get_news(self, *_):
        """
        Fetch top science and tech news and speak them aloud.
        """
        news_articles = await fetch_top_news()

        if isinstance(news_articles, str):  # Check for error message
            await self.response_manager.speak_with_flite(f"News fetch failed: {news_articles}")
        else:
            # Play the weather intro sound
            await self.passive_sound.play_weather_intro_sound()
            # Store headlines in conversation history for potential reference by the LLM
            formatted_news = "Here are today’s top science and tech headlines:\n" + "\n".join(news_articles)
            self.llm_client.conversation_history.append({"role": "system", "content": formatted_news})
            # Speak each news article aloud
            for article in news_articles:
                await self.response_manager.speak_with_flite(article)
    