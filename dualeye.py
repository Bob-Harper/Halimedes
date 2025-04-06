import spidev
import RPi.GPIO as GPIO
import time

class GC9D01Display:
    def __init__(self, cs_pin, dc_pin, rst_pin, bl_pin=None, spi_bus=0, spi_dev=0, spi_speed=40000000):
        # Save pin configuration
        self.cs_pin = cs_pin      # Chip select (CS) for this display
        self.dc_pin = dc_pin      # Data/Command control pin
        self.rst_pin = rst_pin    # Reset pin
        self.bl_pin = bl_pin      # Backlight pin (optional)
        # Set up GPIO
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        GPIO.setup(self.cs_pin, GPIO.OUT, initial=GPIO.HIGH)   # CS inactive (HIGH)
        GPIO.setup(self.dc_pin, GPIO.OUT, initial=GPIO.HIGH)   # D/C (arbitrary initial)
        GPIO.setup(self.rst_pin, GPIO.OUT, initial=GPIO.HIGH)  # RST (will toggle)
        if self.bl_pin is not None:
            GPIO.setup(self.bl_pin, GPIO.OUT, initial=GPIO.HIGH)  # BL on by default
        # Set up SPI interface
        self.spi = spidev.SpiDev()
        self.spi.open(spi_bus, spi_dev)
        self.spi.max_speed_hz = spi_speed
        self.spi.mode = 0        # SPI mode 0 (CPOL=0, CPHA=0)&#8203;:contentReference[oaicite:8]{index=8}
        self.spi.no_cs = True    # We will manually control CS via GPIO
        # Reset the display hardware
        self.reset()
    
    def reset(self):
        """Hardware reset the display."""
        GPIO.output(self.rst_pin, GPIO.LOW)
        time.sleep(0.05)  # 50 ms low
        GPIO.output(self.rst_pin, GPIO.HIGH)
        time.sleep(0.05)  # 50 ms after rising, allow reset complete

    def send_command(self, cmd):
        """Send a single-byte command over SPI (with DC low)."""
        GPIO.output(self.cs_pin, GPIO.LOW)
        GPIO.output(self.dc_pin, GPIO.LOW)
        self.spi.xfer2([cmd & 0xFF])
        GPIO.output(self.cs_pin, GPIO.HIGH)
    
    def send_data(self, data_bytes):
        """Send data bytes over SPI (with DC high)."""
        GPIO.output(self.cs_pin, GPIO.LOW)
        GPIO.output(self.dc_pin, GPIO.HIGH)
        # data_bytes can be a list or bytearray
        self.spi.xfer2(list(data_bytes))
        GPIO.output(self.cs_pin, GPIO.HIGH)
    
    def init_display(self):
        """Send the GC9D01 initialization sequence (from Waveshare demo code)."""
        # ** Initialization sequence (commands & data) extracted from Waveshare's demo :contentReference[oaicite:9]{index=9}&#8203;:contentReference[oaicite:10]{index=10} **
        # Enter extended command mode:
        self.send_command(0xFE)
        self.send_command(0xEF)
        # Set registers 0x80 to 0x8F to 0xFF (recommended init for this panel):
        for reg in range(0x80, 0x90):  # 0x80 through 0x8F
            self.send_command(reg)
            self.send_data([0xFF])
        # Interface pixel format: 0x05 = 16-bit/pixel (65K colors)&#8203;:contentReference[oaicite:11]{index=11}
        self.send_command(0x3A); self.send_data([0x05])
        # Additional panel configuration commands:
        self.send_command(0xEC); self.send_data([0x01])
        self.send_command(0x74)
        self.send_data([0x02, 0x0E, 0x00, 0x00, 0x00, 0x00])
        self.send_command(0x98); self.send_data([0x3E])
        self.send_command(0x99); self.send_data([0x3E])
        self.send_command(0xB5); self.send_data([0x0D, 0x0D])
        # Set voltage, VCOM, and gamma-related registers (power/gamma tuning):
        self.send_command(0x60); self.send_data([0x38, 0x0F, 0x79, 0x67])
        self.send_command(0x61); self.send_data([0x38, 0x11, 0x79, 0x67])
        self.send_command(0x64); self.send_data([0x38, 0x17, 0x71, 0x5F, 0x79, 0x67])
        self.send_command(0x65); self.send_data([0x38, 0x13, 0x71, 0x5B, 0x79, 0x67])
        self.send_command(0x6A); self.send_data([0x00, 0x00])
        self.send_command(0x6C); self.send_data([0x22, 0x02, 0x22, 0x02, 0x22, 0x22, 0x50])
        self.send_command(0x6E)
        self.send_data([0x03, 0x03, 0x01, 0x01, 0x00, 0x00, 0x0F, 0x0F, 0x0D, 0x0D, 0x0B, 0x0B, 0x09])
        # Fine-tune panel timings, driving strength, etc.:
        self.send_command(0xBF); self.send_data([0x01])
        self.send_command(0xF9); self.send_data([0x40])
        self.send_command(0x9B); self.send_data([0x3B])
        self.send_command(0x93); self.send_data([0x33, 0x7F, 0x00])
        self.send_command(0x7E); self.send_data([0x30])
        self.send_command(0x70); self.send_data([0x0D, 0x02, 0x08, 0x0D, 0x02, 0x08])
        self.send_command(0x71); self.send_data([0x0D, 0x02, 0x08])
        self.send_command(0x91); self.send_data([0x0E, 0x09])
        self.send_command(0xC3); self.send_data([0x19])
        self.send_command(0xC4); self.send_data([0x19])
        self.send_command(0xC9); self.send_data([0x3C])
        # Gamma correction registers (positive & negative gamma curves)&#8203;:contentReference[oaicite:12]{index=12}:
        """original default values:
        self.send_command(0xF0); self.send_data([0x53, 0x15, 0x0A, 0x04, 0x00, 0x3E])
        self.send_command(0xF2); self.send_data([0x53, 0x15, 0x0A, 0x04, 0x00, 0x3A])
        self.send_command(0xF1); self.send_data([0x56, 0xA8, 0x7F, 0x33, 0x34, 0x5F])
        self.send_command(0xF3); self.send_data([0x52, 0xA4, 0x7F, 0x33, 0x34, 0xDF])
        """
        self.send_command(0xF0); self.send_data([0x54, 0x15, 0x0A, 0x04, 0x00, 0x3E])  # Positive gamma
        self.send_command(0xF2); self.send_data([0x53, 0x15, 0x0A, 0x04, 0x00, 0x3A])  # Positive gamma
        self.send_command(0xF1)
        self.send_data([0x5A, 0xA8, 0x7F, 0x33, 0x34, 0x5F])
        self.send_command(0xF3)
        self.send_data([0x56, 0xA4, 0x7F, 0x33, 0x34, 0xDF])
        # Memory access control (orientation, color order):
        self.send_command(0x36); self.send_data([0x00])
        # ^ 0x36=0x00 sets default rotation and RGB color order. If red/blue are swapped, use 0x36=0x08.
        # Sleep out & display on:
        self.send_command(0x11)   # Sleep Out
        time.sleep(0.120)         # Wait 120ms (minimum 120ms required after 0x11)&#8203;:contentReference[oaicite:13]{index=13}
        self.send_command(0x29)   # Display ON
        # The screen is now initialized and ready to receive pixel data.
    
    def set_address_window(self, x0, y0, x1, y1):
        """Set the address window (column x0..x1, row y0..y1) for subsequent pixel writes."""
        # Column address set (0x2A): send start and end column (each 16-bit)
        self.send_command(0x2A)
        self.send_data([ (x0>>8)&0xFF, x0 & 0xFF, (x1>>8)&0xFF, x1 & 0xFF ])
        # Row address set (0x2B)
        self.send_command(0x2B)
        self.send_data([ (y0>>8)&0xFF, y0 & 0xFF, (y1>>8)&0xFF, y1 & 0xFF ])
        # Write to RAM (0x2C) - following bytes will be written to GRAM as pixels
        self.send_command(0x2C)
    
    def send_pixels(self, pixel_bytes):
        GPIO.output(self.cs_pin, GPIO.LOW)
        GPIO.output(self.dc_pin, GPIO.HIGH)
        CHUNK_SIZE = 640  # maximum bytes per transfer
        for i in range(0, len(pixel_bytes), CHUNK_SIZE):
            chunk = pixel_bytes[i:i+CHUNK_SIZE]
            self.spi.xfer2(list(chunk))
        GPIO.output(self.cs_pin, GPIO.HIGH)


def fill_screen_color(display, color):
    width = 160
    height = 160
    pixel_buffer = bytearray()
    for _ in range(width * height):
        pixel_buffer.append((color >> 8) & 0xFF)
        pixel_buffer.append(color & 0xFF)
    display.set_address_window(0, 0, width - 1, height - 1)
    display.send_pixels(pixel_buffer)


def draw_color_stripes(display):
    width = 160
    height = 160
    stripe_width = width // 6
    pixel_buffer = bytearray()
    for y in range(height):
        for x in range(width):
            if x < stripe_width:
                color = 0xF800  # Red
            elif x < 2 * stripe_width:
                color = 0x07E0  # Green
            elif x < 3 * stripe_width:
                color = 0x001F  # Blue
            elif x < 4 * stripe_width:
                color = 0xFFE0  # Yellow
            elif x < 5 * stripe_width:
                color = 0x07FF  # Cyan
            else:
                color = 0xF81F  # Magenta
            pixel_buffer.append((color >> 8) & 0xFF)
            pixel_buffer.append(color & 0xFF)
    display.set_address_window(0, 0, width - 1, height - 1)
    display.send_pixels(pixel_buffer)

"""
FrankenSPI through 40pin splitter because Hat is a Pin Hog
Label	Wire Color	Pin #	GPIO /  Function Description Notes
VCC	    Red	        1	    3.3V    Power	Main power for both eyes
GND	    Black	    6	    Ground	Common ground
CS2	    Green	    8	    GPIO14  TXD	Right eye chip select
RST1	Yellow	    18	    GPIO24	Left eye reset
BL2	    Grey	    HAT	    3v3     Right backlight 
DIN	    Brown	    21	    GPIO9   MISO	SPI data in
CLK	    Purple	    23	    GPIO11  SCLK	SPI clock
CS1	    Blue	    31	    GPIO6	Left eye chip select
DC	    Orange	    33	    GPIO13	Data/Command line
RST2	White	    38	    GPIO20	Right eye reset 
BL1	    B/W	        17	    3v3     Left backlight 
"""