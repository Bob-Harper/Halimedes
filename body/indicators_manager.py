# body/indicators_manager.py
import asyncio

class IndicatorsManager:
    def __init__(self, led):
        self.led = led
        self.mode = "idle"
        self._task = None

    def start(self):
        if self._task is None:
            self._task = asyncio.create_task(self._run())

    def set_mode(self, mode: str):
        self.mode = mode

    async def _run(self):
        while True:
            if self.mode == "idle":
                self.led.on()
                await asyncio.sleep(0.1)
                self.led.off()
                await asyncio.sleep(1.9)

            elif self.mode == "busy":
                self.led.on()
                await asyncio.sleep(0.1)

            elif self.mode == "off":
                self.led.off()
                await asyncio.sleep(0.1)

            else:
                self.led.off()
                await asyncio.sleep(0.1)
