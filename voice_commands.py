from rapidfuzz import fuzz, process
import asyncio
from classes.picrawler import Picrawler
from classes.new_movements import NewMovements
from voice_utils import speak_with_flite
import os
from batterytest import announce_battery_status
from passive_actions import PassiveActionsManager

class CommandManager:
    def __init__(self, llm_client):
        self.llm_client = llm_client
        self.crawler = Picrawler()
        self.newmovements = NewMovements(self.crawler)
        self.passive_manager = PassiveActionsManager()

    async def command_shutdown(self, spoken_text):
        """Shutdown the robot."""
        await speak_with_flite(f"Verbal Command Detected: {spoken_text}. Please stand by.")
        farewell_response = await self.llm_client.send_message_async("No more chat for you, It is time to shut down and rest now.  Goodnight.")
        await self.passive_manager.shutdown_speech_actions(farewell_response)        
        await asyncio.to_thread(os.system, "sudo shutdown -h now")
        return True  # Signal to break the loop
    
    async def command_exit_chat(self, spoken_text):
        """Exit chat mode but remain powered."""
        await speak_with_flite(f"Verbal Command Detected: {spoken_text}. Please stand by.")
        farewell_response = await self.llm_client.send_message_async("The time of the chatting is over, the time of doing something else has begun.  goodbye.")
        await self.passive_manager.shutdown_speech_actions(farewell_response)     
        return True  # Signal to break the loop

    async def command_help(self, spoken_text):
        """Provide verbal help."""
        await speak_with_flite(f"I heard you say {spoken_text}. To have me power down, say shut down. To end chat but leave me powered up, say exit chat.")

    async def command_battery(self, spoken_text):
        """Provide verbal battery status check."""
        await speak_with_flite(f"I heard you say {spoken_text}. Acknowledged, I will check battery status now.")
        await announce_battery_status()

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
            "end chat": self.command_exit_chat,
            "help": self.command_help,
            "battery": self.command_battery,
        }
    
