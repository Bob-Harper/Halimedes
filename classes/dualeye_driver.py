#!/usr/bin/env python3
import time
import spidev
import RPi.GPIO as GPIO
from gc9d01_library import GC9D01
import types  # For clean method binding

# ---- HELPER METHODS TO BIND TO `eye` ----

def draw_pixel(self, x, y, color):
    if 0 <= x < 160 and 0 <= y < 160:
        self.set_window(x, y, x, y)
        hi = (color >> 8) & 0xFF
        lo = color & 0xFF
        self.write_data(bytes([hi, lo]))

def fill_rect(self, x, y, w, h, color):
    if w <= 0 or h <= 0:
        return
    x1 = min(x + w - 1, 159)
    y1 = min(y + h - 1, 159)
    self.set_window(x, y, x1, y1)
    hi = (color >> 8) & 0xFF
    lo = color & 0xFF
    buf = bytes([hi, lo]) * (w * h)
    for i in range(0, len(buf), 1024):
        self.write_data(buf[i:i+1024])

def fill_screen_safely(self, color, chunk_size=1024):
    width, height = 160, 160
    hi = (color >> 8) & 0xFF
    lo = color & 0xFF
    pixel = bytes([hi, lo])
    buf = pixel * (width * height)
    self.set_window(0, 0, width - 1, height - 1)
    for i in range(0, len(buf), chunk_size):
        self.write_data(buf[i:i + chunk_size])

# ---- SPI + GPIO SETUP ----

class VirtualIO:
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
        if isinstance(data, (bytes, bytearray)):
            self._spi.xfer2(list(data))
        elif isinstance(data, list):
            self._spi.xfer2(data)
        else:
            raise ValueError(f"Unsupported SPI write type: {type(data)}")

    def __getattr__(self, name):
        return getattr(self._spi, name)

# ---- DISPLAY PATCH ----

def apply_display_patch(patched=True):
    try:
        if patched:
            # print("Applying GC9D01 pixel + porch timing fix...")
            # Falling edge pixel clock
            eye_left.write_cmd(0xB0, bytes([0x00]))
            eye_right.write_cmd(0xB0, bytes([0x00]))
        else:
            # print("Reverting to default GC9D01 timing...")
            eye_left.write_cmd(0xB0, bytes([0x08]))
            eye_right.write_cmd(0xB0, bytes([0x08]))
    except Exception as e:
        print(f"Patch failed: {e}")

# ---- INIT DISPLAY ----

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

LEFT_EYE = {
    'cs': 6,
    'dc': 13,
    'rst': 24
}

cs = VirtualIO(LEFT_EYE['cs'])
dc = VirtualIO(LEFT_EYE['dc'])
rst = VirtualIO(LEFT_EYE['rst'])

spi = SPIWrapper()

# Existing setup...
eye_left = GC9D01(spi, dc=dc, cs=cs, rst=rst)
eye_left.set_rotation(1)

RIGHT_EYE = {
    'cs': 14,
    'dc': 13,  # shared with left
    'rst': 20
}

cs_r = VirtualIO(RIGHT_EYE['cs'])
dc_r = VirtualIO(RIGHT_EYE['dc'])
rst_r = VirtualIO(RIGHT_EYE['rst'])

eye_right = GC9D01(spi, dc=dc_r, cs=cs_r, rst=rst_r)
eye_right.set_rotation(3)
#eye_right.write_cmd(0x36, bytes([0x60]))               # MADCTL: MV=0, MX=1, MY=1


apply_display_patch(True)

# ---- METHOD PATCHES (BOUND TO `eye`) ----

eye_right.draw_pixel = types.MethodType(draw_pixel, eye_right)
eye_right.fill_rect = types.MethodType(fill_rect, eye_right)
eye_right.fill_screen = types.MethodType(fill_screen_safely, eye_right)

eye_left.draw_pixel = types.MethodType(draw_pixel, eye_left)
eye_left.fill_rect = types.MethodType(fill_rect, eye_left)
eye_left.fill_screen = types.MethodType(fill_screen_safely, eye_left)

# ---- TEST MODE (Optional) ----

if __name__ == "__main__":
    print("Running built-in display test...")
    eye_left.fill_screen(0x07FF)   # Cyan
    eye_right.fill_screen(0xF81F)  # Magenta

    eye_left.draw_pixel(80, 80, 0xFFFF)  # White pixel center
    eye_right.draw_pixel(80, 80, 0xFFFF)
    colors = [
        ("Red", 0xF800),
        ("Green", 0x07E0),
        ("Blue", 0x001F),
        ("White", 0xFFFF),
        ("Black", 0x0000)
    ]
    for name, color in colors:
        print(f"Filling with {name}")
        eye_right.fill_screen(color)
        eye_left.fill_screen(color)
        time.sleep(0.8)


"""
FrankenSPI through 40-pin splitter (Robot Hat is a Pin Hog)

Label   Wire Color  Phys Pin  GPIO #   Function / Description                   Notes
------  ----------- --------- -------- ---------------------------------------- ------------------------------
VCC     Red         1         —        3.3V Power                               Main power for both eyes
GND     Black       6         —        Ground                                   Common ground
CS2     Green       8         14       Chip Select - RIGHT eye (EYE2)           Use for right eye control
RST1    Yellow      18        24       Reset Line - LEFT eye (EYE1)             Use with cs_pin=6
BL2     Grey        17        —        3.3V for backlight (powers **both**)     Use this only. see bottom note
DIN     Brown       *19*     *10*      **SPI MOSI data *to* display**           MUST be GPIO10 / Pin 19!
CLK     Purple      23        11       SPI Clock (SCLK)                         Standard SPI clock line
CS1     Blue        31        6        Chip Select - LEFT eye (EYE1)            Use for left eye control
DC      Orange      33        13       Data/Command Line                        Required for both eyes
RST2    White       38        20       Reset Line - RIGHT eye (EYE2)            Use with cs_pin=14
BL1     B/W         N/A       —        [UNUSED] Left backlight input            Do not use, see bottom note

NOTE:BL2 powers both displays at once.  It is the only one you should use.
BL1 is for advanced control of the left eye's backlight.  It is not used in this code.

"""