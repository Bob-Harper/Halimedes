import asyncio
import random
from classes.picrawler import Picrawler
from classes.new_movements import NewMovements
from voice_utils import speak_with_flite
import os

class CommandManager:
    def __init__(self, llm_client):
        self.llm_client = llm_client
        self.crawler = Picrawler()
        self.newmovements = NewMovements(self.crawler)

    async def command_shutdown(self, spoken_text):
        """Shutdown the robot."""
        await speak_with_flite(f"Verbal Command Detected: {spoken_text}. Please stand by.")
        farewell_response = await self.llm_client.send_message_async("No more chat for you, It is time to shut down and rest now.  Goodnight.")
        await speak_with_flite(farewell_response)
        await asyncio.to_thread(os.system, "sudo shutdown -h now")
        return True  # Signal to break the loop
    
    async def command_exit_chat(self, spoken_text):
        """Exit chat mode but remain powered."""
        await speak_with_flite(f"Verbal Command Detected: {spoken_text}. Please stand by.")
        farewell_response = await self.llm_client.send_message_async("The time of the chatting is over, the time of doing something else has begun.  goodbye.")
        await speak_with_flite(farewell_response)
        return True  # Signal to break the loop

    async def command_help(self, spoken_text):
        """Provide verbal help."""
        await speak_with_flite(f"I heard you say {spoken_text}. To have me power down, say shut down. To end chat but leave me powered up, say exit chat.")

    @property
    def command_map(self):
        return {
            "shut down": self.command_shutdown,
            "shutdown": self.command_shutdown,
            "power dow": self.command_shutdown,
            "power off": self.command_shutdown,
            "standby": self.command_shutdown,
            "go to bed": self.command_shutdown,
            "exit chat": self.command_exit_chat,
            "goodbye": self.command_exit_chat,
            "goodnight": self.command_exit_chat,
            "end chat": self.command_exit_chat,
            "quit": self.command_exit_chat,
            "quit chat": self.command_exit_chat,
            "exit": self.command_exit_chat,
            "shush": self.command_exit_chat,
            "good bye": self.command_exit_chat,
            "good night": self.command_exit_chat,
            "help": self.command_help,
            "what": self.command_help,
            "what do i do": self.command_help,
            "help me": self.command_help,
            "help": self.command_help,
        }
