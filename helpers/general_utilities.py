import asyncio
import aiofiles
from robot_hat.utils import get_battery_voltage
from helpers.response_utils import Response_Manager


class GeneralUtilities:
    def __init__(self, picrawler_instance):
        self.picrawler_instance = picrawler_instance
        self.response_manager = Response_Manager(self.picrawler_instance)

    @staticmethod
    async def log_response_to_file(response_text, log_file="hal_responses.log"):
        """Logs the response text asynchronously to a file."""
        try:
            async with aiofiles.open(log_file, 'a') as file:
                await file.write(response_text + "\n\n")
        except Exception as e:
            print(f"Error writing to log file: {e}")

    # --- Battery Management ---
    async def get_battery_status(self, max_retries=3, retry_delay=2):
        """Get the battery voltage with retries and classify the status."""
        for attempt in range(max_retries):
            await self.response_manager.speak_with_flite(f"Battery Check {attempt + 1}.")
            voltage = get_battery_voltage()
            if voltage > 0:
                break
            await asyncio.sleep(retry_delay)

        if voltage <= 0:  # Still 0 after retries
            voltage = 0
            status = "Unknown"
        else:
            if voltage > 7.6:
                status = "Full"
            elif 7.15 <= voltage <= 7.6:
                status = "Medium"
            elif 6.9 <= voltage < 7.15:
                status = "Low"
            else:
                status = "Critical"

        return voltage, status

    async def announce_battery_status(self):
        """Announce the current battery voltage and status."""
        voltage, status = await self.get_battery_status()
        await self.response_manager.speak_with_flite(f"My battery is currently at {voltage:.2f} volts. Status: {status}.")
        if status == "Low":
            await self.response_manager.speak_with_flite("Please monitor power levels closely and consider power pack recharge.")
        elif status == "Critical": 
            await self.response_manager.speak_with_flite("Warning! Immediate power pack recharge recommended, imminent shutdown possibility.")
        elif status == "Unknown":  
            await self.response_manager.speak_with_flite("Battery not detected. Proceed with caution, recheck battery status regularly.")

