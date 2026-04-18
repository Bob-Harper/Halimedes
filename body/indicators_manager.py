from helpers.global_config import LED_INDICATOR, SOUND_ASSETS_PATH 
import asyncio



async def _led_blip(self):
    """Blinks the LED every 2 seconds while listening."""
    while True:
        self.listening_led.on()
        await asyncio.sleep(0.1)
        self.listening_led.off()
        await asyncio.sleep(1.9)