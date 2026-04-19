#!/usr/bin/env python3
import time
import spidev
import RPi.GPIO as GPIO
from gc9d01_library import GC9D01

# ---- PATCH ----
class FakeDigitalIO:
    def __init__(self, gpio_num):
        self.gpio = gpio_num
        GPIO.setup(self.gpio, GPIO.OUT)
    @property
    def direction(self): return None
    @direction.setter
    def direction(self, value): pass
    @property
    def value(self): return GPIO.input(self.gpio)
    @value.setter
    def value(self, val): GPIO.output(self.gpio, GPIO.HIGH if val else GPIO.LOW)

class SPIWrapper:
    def __init__(self, bus=0, device=0, max_hz=40000000):
        self._spi = spidev.SpiDev()
        self._spi.open(bus, device)
        self._spi.max_speed_hz = max_hz
        self._spi.mode = 0

    def write(self, data):
        if isinstance(data, bytes):
            self._spi.xfer2(list(data))
        elif isinstance(data, list):
            self._spi.xfer2(data)
        else:
            raise ValueError("Unsupported SPI write type")

    def __getattr__(self, name):
        # Forward any unknown attributes to the underlying SpiDev
        return getattr(self._spi, name)
    
# ---- GPIO SETUP ----
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

# Pin numbers
LEFT_EYE = {
    'cs': 6,
    'dc': 13,
    'rst': 24
}

# Wrap GPIO in fake digitalio-style objects
cs = FakeDigitalIO(LEFT_EYE['cs'])
dc = FakeDigitalIO(LEFT_EYE['dc'])
rst = FakeDigitalIO(LEFT_EYE['rst'])

# ---- INIT DISPLAY ----
spi = SPIWrapper()  # instead of spidev.SpiDev()

eye = GC9D01(spi, dc=dc, cs=cs, rst=rst)

# ---- PATCH fill_screen ----
def fill_screen_safely(display, color, chunk_size=4096):
    width, height = 160, 160
    total_pixels = width * height
    hi = (color >> 8) & 0xFF
    lo = color & 0xFF
    pixel = bytes([hi, lo])
    buf = pixel * total_pixels

    display.set_window(0, 0, width - 1, height - 1)

    for i in range(0, len(buf), chunk_size):
        display.write_data(buf[i:i+chunk_size])

# Monkeypatch it
eye.fill_screen = lambda color: fill_screen_safely(eye, color)

# ---- TEST PATTERNS ----
def cycle_colors():
    colors = {
        "Red":    0xF800,
        "Green":  0x07E0,
        "Blue":   0x001F,
        "White":  0xFFFF,
        "Yellow": 0xFFE0,
        "Cyan":   0x07FF,
        "Magenta": 0xF81F,
        "Black":  0x0000
    }
    for name, color in colors.items():
        print(f"Filling with {name}")
        eye.fill_screen(color)
        time.sleep(0.8)

# ---- RUN ----
if __name__ == "__main__":
    cycle_colors()
    print("All hail the glowing orb.")
