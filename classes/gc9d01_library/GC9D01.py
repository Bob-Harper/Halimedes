import digitalio
import time
import logging

logger = logging.getLogger(__name__)

try:
    from font5x7 import FONT_5X7
except ImportError:
    FONT_5X7 = {}

class GC9D01Error(Exception):
    """Base exception class for GC9D01 errors."""
    pass

class GC9D01:
    """
    A driver for the GC9D01 round LCD display.
    
    This class provides methods to initialize and control a GC9D01 display
    connected to a Raspberry Pi via SPI.
    """

    def __init__(self, spi, dc, cs, rst):
        """
        Initialize the GC9D01 display.

        Args:
            spi (SPI): The SPI interface
            dc (DigitalInOut): The data/command pin
            cs (DigitalInOut): The chip select pin
            rst (DigitalInOut): The reset pin

        Raises:
            GC9D01Error: If initialization fails
        """
        try:
            self.spi = spi
            self.dc = dc
            self.cs = cs
            self.rst = rst
            self.width = 160
            self.height = 160

            self.dc.direction = digitalio.Direction.OUTPUT
            self.cs.direction = digitalio.Direction.OUTPUT
            self.rst.direction = digitalio.Direction.OUTPUT

            self.init_display()
            self.set_rotation(0)  # Set initial rotation to normal
        except Exception as e:
            raise GC9D01Error(f"Failed to initialize display: {str(e)}")

    def init_display(self):
        """
        Initialize the display with the required commands.

        Raises:
            GC9D01Error: If initialization fails
        """
        try:
            logger.debug("Initializing display...")
            self.reset()
            
            # Send initialization commands to the display
            # Each write_cmd call sends a command to the display
            # Some commands are followed by data bytes
            self.write_cmd(0xFE)
            self.write_cmd(0xEF)
            
            self.write_cmd(0x80, b'\xFF')
            self.write_cmd(0x81, b'\xFF')
            self.write_cmd(0x82, b'\xFF')
            self.write_cmd(0x83, b'\xFF')
            self.write_cmd(0x84, b'\xFF')
            self.write_cmd(0x85, b'\xFF')
            self.write_cmd(0x86, b'\xFF')
            self.write_cmd(0x87, b'\xFF')
            self.write_cmd(0x88, b'\xFF')
            self.write_cmd(0x89, b'\xFF')
            self.write_cmd(0x8A, b'\xFF')
            self.write_cmd(0x8B, b'\xFF')
            self.write_cmd(0x8C, b'\xFF')
            self.write_cmd(0x8D, b'\xFF')
            self.write_cmd(0x8E, b'\xFF')
            self.write_cmd(0x8F, b'\xFF')
            
            self.write_cmd(0x3A, b'\x05')
            self.write_cmd(0xEC, b'\x01')
            
            self.write_cmd(0x74, b'\x02', b'\x0E', b'\x00', b'\x00', b'\x00', b'\x00', b'\x00')
            
            self.write_cmd(0x98, b'\x3E')
            self.write_cmd(0x99, b'\x3E')
            
            self.write_cmd(0xB5, b'\x0D', b'\x0D')
            
            self.write_cmd(0x60, b'\x38', b'\x0F', b'\x79', b'\x67')
            self.write_cmd(0x61, b'\x38', b'\x11', b'\x79', b'\x67')
            self.write_cmd(0x64, b'\x38', b'\x17', b'\x71', b'\x5F', b'\x79', b'\x67')
            self.write_cmd(0x65, b'\x38', b'\x13', b'\x71', b'\x5B', b'\x79', b'\x67')
            
            self.write_cmd(0x6A, b'\x00', b'\x00')
            self.write_cmd(0x6C, b'\x22', b'\x02', b'\x22', b'\x02', b'\x22', b'\x22', b'\x50')
            
            self.write_cmd(0x6E, b'\x03', b'\x03', b'\x01', b'\x01', b'\x00', b'\x00', b'\x0f', b'\x0f', b'\x0d', b'\x0d', b'\x0b', b'\x0b', b'\x09', b'\x09', b'\x00', b'\x00', b'\x00', b'\x00', b'\x0a', b'\x0a', b'\x0c', b'\x0c', b'\x0e', b'\x0e', b'\x10', b'\x10', b'\x00', b'\x00', b'\x02', b'\x02', b'\x04', b'\x04')
            
            self.write_cmd(0xBF, b'\x01')
            self.write_cmd(0xF9, b'\x40')
            
            self.write_cmd(0x9B, b'\x3B')
            self.write_cmd(0x93, b'\x33', b'\x7F', b'\x00')
            
            self.write_cmd(0x7E, b'\x30')
            
            self.write_cmd(0x70, b'\x0D', b'\x02', b'\x08', b'\x0D', b'\x02', b'\x08')
            self.write_cmd(0x71, b'\x0D', b'\x02', b'\x08')
            
            self.write_cmd(0x91, b'\x0E', b'\x09')
            
            self.write_cmd(0xC3, b'\x1F')  # VREG1A voltage control
            self.write_cmd(0xC4, b'\x1F')  # VREG1B voltage control
            self.write_cmd(0xC9, b'\x1F')  # VREG2A voltage control
            
            self.write_cmd(0xF0, b'\x53', b'\x15', b'\x0A', b'\x04', b'\x00', b'\x3E')
            self.write_cmd(0xF2, b'\x53', b'\x15', b'\x0A', b'\x04', b'\x00', b'\x3A')
            self.write_cmd(0xF1, b'\x56', b'\xA8', b'\x7F', b'\x33', b'\x34', b'\x5F')
            self.write_cmd(0xF3, b'\x52', b'\xA4', b'\x7F', b'\x33', b'\x34', b'\xDF')
            
            self.write_cmd(0x36, b'\xC8')  # Memory Access Control (rotate 180 degrees)
            self.write_cmd(0x3A, b'\x05')  # Set color mode (16-bit color)
            self.write_cmd(0xB0, b'\x00')  # Set addressing mode (0x00 for horizontal)
            self.write_cmd(0xB1, b'\x00', b'\x00')  # Set frame rate (default)
            self.write_cmd(0xB4, b'\x00')  # Display inversion control (default)
            
            self.write_cmd(0x11)  # Sleep out
            time.sleep(0.200)  # 200ms delay
            
            self.write_cmd(0x29)  # Display on
            self.write_cmd(0x2C)  # Memory write
            
            logger.debug("Display initialization complete.")
        except Exception as e:
            raise GC9D01Error(f"Display initialization failed: {str(e)}")

    def reset(self):
        """
        Perform a hardware reset on the display.

        Raises:
            GC9D01Error: If reset fails
        """
        try:
            self.rst.value = 0
            time.sleep(0.1)
            self.rst.value = 1
            time.sleep(0.1)
        except Exception as e:
            raise GC9D01Error(f"Failed to reset display: {str(e)}")

    def write_cmd(self, cmd, *data):
        """
        Write a command to the display.

        Args:
            cmd (int): The command byte
            *data: Optional data bytes to send after the command

        Raises:
            GC9D01Error: If writing command fails
        """
        try:
            self.dc.value = 0
            self.cs.value = 0
            self.spi.write(bytes([cmd]))
            self.cs.value = 1
            if data:
                self.write_data(b''.join(data))
        except Exception as e:
            raise GC9D01Error(f"Failed to write command: {str(e)}")

    def write_data(self, data):
        """
        Write data to the display.

        Args:
            data (bytes): The data to write

        Raises:
            GC9D01Error: If writing data fails
        """
        try:
            logger.debug(f"Writing data: {data[:10]}... (total {len(data)} bytes)")
            self.dc.value = 1
            self.cs.value = 0
            self.spi.write(data)
            self.cs.value = 1
        except Exception as e:
            raise GC9D01Error(f"Failed to write data: {str(e)}")

    def set_window(self, x0, y0, x1, y1):
        """
        Set the active window on the display using absolute addressing.

        Args:
            x0 (int): Start X coordinate
            y0 (int): Start Y coordinate
            x1 (int): End X coordinate
            y1 (int): End Y coordinate

        Raises:
            GC9D01Error: If setting window fails
            ValueError: If coordinates are out of bounds
        """
        if not (0 <= x0 <= x1 < self.width and 0 <= y0 <= y1 < self.height):
            raise ValueError(f"Invalid window coordinates: ({x0}, {y0}) to ({x1}, {y1})")
        try:
            logger.debug(f"Setting window: ({x0}, {y0}) to ({x1}, {y1})")
            self.write_cmd(0x2A, bytes([x0 >> 8, x0 & 0xFF, x1 >> 8, x1 & 0xFF]))
            self.write_cmd(0x2B, bytes([y0 >> 8, y0 & 0xFF, y1 >> 8, y1 & 0xFF]))
            self.write_cmd(0x2C)
        except Exception as e:
            raise GC9D01Error(f"Failed to set window: {str(e)}")

    def fill_screen(self, color):
        """
        Fill the entire screen with a single color.

        Args:
            color (int): 16-bit RGB565 color value

        Raises:
            GC9D01Error: If filling screen fails
            ValueError: If color value is invalid
        """
        if not 0 <= color <= 0xFFFF:
            raise ValueError("Invalid color value")
        try:
            self.set_window(0, 0, self.width - 1, self.height - 1)
            color_bytes = color.to_bytes(2, 'big')
            data = color_bytes * (self.width * self.height)
            self.write_data(data)
        except Exception as e:
            raise GC9D01Error(f"Failed to fill screen: {str(e)}")

    def draw_pixel(self, x, y, color):
        """
        Draw a single pixel at the specified position.

        Args:
            x (int): X coordinate
            y (int): Y coordinate
            color (int): 16-bit RGB565 color value

        Raises:
            GC9D01Error: If drawing pixel fails
            ValueError: If coordinates are out of bounds or color is invalid
        """
        if not (0 <= x < self.width and 0 <= y < self.height):
            raise ValueError(f"Coordinates out of bounds: ({x}, {y})")
        if not 0 <= color <= 0xFFFF:
            raise ValueError("Invalid color value")
        try:
            self.set_window(x, y, x, y)
            self.write_data(color.to_bytes(2, 'big'))
        except Exception as e:
            raise GC9D01Error(f"Failed to draw pixel: {str(e)}")

    def display_image(self, image_data):
        """
        Display a full-screen image.

        Args:
            image_data (bytes): Raw image data in RGB565 format

        Raises:
            GC9D01Error: If displaying image fails
            ValueError: If image data size is incorrect
        """
        if len(image_data) != self.width * self.height * 2:
            raise ValueError("Invalid image data size")
        try:
            self.set_window(0, 0, self.width - 1, self.height - 1)
            self.write_data(image_data)
        except Exception as e:
            raise GC9D01Error(f"Failed to display image: {str(e)}")

    def set_rotation(self, rotation):
        """
        Set the display rotation.
        
        Args:
            rotation (int): 0 for normal, 1 for 90 degrees, 2 for 180 degrees, 3 for 270 degrees
        """
        if rotation not in [0, 1, 2, 3]:
            raise ValueError("Rotation must be 0, 1, 2, or 3")

        rotation_commands = [
            b'\x00',  # Normal orientation
            b'\x60',  # Rotate 90 degrees
            b'\xC0',  # Rotate 180 degrees
            b'\xA0',  # Rotate 270 degrees
        ]

        self.write_cmd(0x36, rotation_commands[rotation])
        time.sleep(0.1)

        # Update width and height if necessary
        if rotation in [1, 3]:
            self.width, self.height = self.height, self.width

    def draw_char(self, x, y, char, color, scale=1):
        """Draw a single character at the specified position."""
        if char not in FONT_5X7:
            return
        
        for row in range(7):
            for col in range(5):
                if FONT_5X7[char][col] & (1 << (6 - row)):
                    for i in range(scale):
                        for j in range(scale):
                            self.draw_pixel(x + col * scale + i, y + row * scale + j, color)

    def draw_text(self, x, y, text, color, scale=1):
        """Draw text at the specified position."""
        for i, char in enumerate(text):
            self.draw_char(x + i * 6 * scale, y, char.upper(), color, scale)

    def set_brightness(self, brightness):
        """
        Set display brightness level (0-255)
        :param brightness: Brightness level (0-255)
        """
        brightness = max(0, min(255, int(brightness)))  # Clamp between 0-255
        self.write_cmd(0x53)  # WRCTRLD
        self.write_cmd(0x24)     # Enable brightness control
        self.write_cmd(0x51)  # WRDISBV (Write Display Brightness)
        self.write_data(brightness.to_bytes(1, 'big'))
