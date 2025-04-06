#!/usr/bin/env python3
import re
import time
import math
from dualeye import GC9D01Display
from PIL import Image

def rgb565_to_rgb888(color):
    """Convert a 16-bit RGB565 value to an (R, G, B) tuple in 8-bit per channel."""
    r = (color >> 11) & 0x1F
    g = (color >> 5) & 0x3F
    b = color & 0x1F
    # Scale to 8-bit values:
    r = (r * 255) // 31
    g = (g * 255) // 63
    b = (b * 255) // 31
    return (r, g, b)

def load_rgb565_image_pil(array_name, width, height, filename="eyes/owlEye.h"):
    """
    Loads a 16-bit RGB565 image from the specified array in a .h file
    and returns a PIL Image in "RGB" mode.
    """
    with open(filename, "r") as f:
        data = f.read()
    # Regex to capture the array contents for a given array name
    pattern = r'const\s+uint16_t\s+' + array_name + r'\s*\[[^\]]+\]\s+PROGMEM\s*=\s*\{([^}]+)\};'
    match = re.search(pattern, data, re.DOTALL)
    if not match:
        print("Array", array_name, "not found in", filename)
        return None
    hex_data = match.group(1)
    # Extract hex numbers like "0xF800"
    hex_values = re.findall(r'0x[0-9A-Fa-f]{4}', hex_data)
    expected = width * height
    if len(hex_values) < expected:
        print("Warning: expected", expected, "pixels in", array_name, "but found", len(hex_values))
    pixels = []
    for i in range(expected):
        value = int(hex_values[i], 16)
        pixels.append(rgb565_to_rgb888(value))
    img = Image.new("RGB", (width, height))
    img.putdata(pixels)
    return img

def pil_to_rgb565_bytearray(img):
    """
    Converts a PIL Image (mode "RGB") to a bytearray containing RGB565 data in big-endian order.
    """
    pixel_data = list(img.getdata())
    buf = bytearray()
    for (r, g, b) in pixel_data:
        # Convert 8-bit RGB to 5-6-5 bits:
        r5 = r >> 3
        g6 = g >> 2
        b5 = b >> 3
        color = (r5 << 11) | (g6 << 5) | b5
        buf.append((color >> 8) & 0xFF)
        buf.append(color & 0xFF)
    return buf

# Initialize the display (adjust GPIO pin numbers as needed)
display = GC9D01Display(cs_pin=6, dc_pin=13, rst_pin=24, bl_pin=None)
display.reset()
display.init_display()

# Load the sclera image (180x180) and crop it to a centered 160x160 area.
sclera_img = load_rgb565_image_pil("sclera", 180, 180)
if sclera_img is None:
    exit(1)
crop_left = (180 - 160) // 2
crop_top  = (180 - 160) // 2
sclera_cropped = sclera_img.crop((crop_left, crop_top, crop_left + 160, crop_top + 160))

# Load the polar image (80x80) which we will use for the iris/pupil.
polar_img = load_rgb565_image_pil("polar", 80, 80)
if polar_img is None:
    exit(1)

# Animation parameters:
num_frames = 40
max_offset = 80  # Maximum horizontal shift (160 - 80)

# Animate the iris movement over the sclera:
for frame in range(num_frames):
    # Compute a smooth horizontal offset using a sine wave.
    # Offset will vary between 0 and max_offset.
    offset = int((math.sin(2 * math.pi * frame / num_frames) + 1) / 2 * max_offset)
    
    # Create a composite image starting with the cropped sclera.
    composite = sclera_cropped.copy()
    # Calculate vertical offset to center the 80x80 polar image (vertical center: (160-80)//2 = 40)
    vertical_offset = 40
    # Paste the polar image (iris) onto the sclera at the computed horizontal offset.
    composite.paste(polar_img, (offset, vertical_offset))
    
    # Convert the composite image to an RGB565 bytearray.
    pixel_buffer = pil_to_rgb565_bytearray(composite)
    
    # Update the display.
    display.set_address_window(0, 0, 159, 159)
    display.send_pixels(pixel_buffer)
    
    time.sleep(0.1)  # Adjust frame rate as desired

input("Animation complete. Press Enter to exit...")
