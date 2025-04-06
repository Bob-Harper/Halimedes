#!/usr/bin/env python3
import re
import time
from dualeye import GC9D01Display


def brighten_pixel(color, factor=1.2):
    """
    Brighten a single 16-bit RGB565 pixel by multiplying its color components
    by the given factor. The factor should be > 1.0 to brighten.
    """
    # Extract the components from 565 format:
    # Red: bits 11-15 (5 bits), Green: bits 5-10 (6 bits), Blue: bits 0-4 (5 bits)
    r = (color >> 11) & 0x1F
    g = (color >> 5) & 0x3F
    b = color & 0x1F

    # Scale each component and clamp to maximum (0x1F for red/blue, 0x3F for green)
    r = min(int(r * factor), 0x1F)
    g = min(int(g * factor), 0x3F)
    b = min(int(b * factor), 0x1F)

    # Reassemble the pixel
    return (r << 11) | (g << 5) | b


def load_image_from_h(filename, array_name, img_width, img_height, crop_width=None, crop_height=None):
    """
    Load a 16-bit RGB565 image from a C header (.h) file.
    
    Parameters:
      filename: The name of the .h file.
      array_name: The name of the array to extract (e.g. "sclera").
      img_width: The declared width of the image in the .h file.
      img_height: The declared height of the image in the .h file.
      crop_width: (Optional) Width to crop to (default = img_width).
      crop_height: (Optional) Height to crop to (default = img_height).
    
    Returns:
      A bytearray of pixel data (big-endian RGB565) for the cropped area.
    """
    with open(filename, "r") as f:
        data = f.read()
    # Use regex to find the block of hex values for the given array.
    pattern = r'const\s+uint16_t\s+' + array_name + r'\s*\[[^\]]+\]\s+PROGMEM\s*=\s*\{([^}]+)\};'
    match = re.search(pattern, data, re.DOTALL)
    if not match:
        print("Array", array_name, "not found in", filename)
        return None
    hex_data = match.group(1)
    # Extract all hex numbers (e.g., "0xF800")
    hex_values = re.findall(r'0x[0-9A-Fa-f]{4}', hex_data)
    expected_pixels = img_width * img_height
    if len(hex_values) < expected_pixels:
        print("Warning: Expected at least", expected_pixels, "pixels in", array_name, "but found", len(hex_values))
    # Set crop dimensions (if not provided, use full image)
    if crop_width is None:
        crop_width = img_width
    if crop_height is None:
        crop_height = img_height
    # Build pixel buffer for the cropped area:
    pixel_buffer = bytearray()
    for row in range(crop_height):
        for col in range(crop_width):
            index = row * img_width + col  # using the full image's row stride
            value = int(hex_values[index], 16)
            value = brighten_pixel(value, factor=0.2)  # Increase factor if needed
            pixel_buffer.append((value >> 8) & 0xFF)  # high byte
            pixel_buffer.append(value & 0xFF)         # low byte
    return pixel_buffer

# Instantiate the display (adjust the GPIO pin numbers as needed):
display = GC9D01Display(cs_pin=6, dc_pin=13, rst_pin=24, bl_pin=None)
display.reset()
display.init_display()

# Load the "sclera" image from owlEye.h.
# The file declares sclera as 180x180, but our display is 160x160, so we crop.
pixel_buffer = load_image_from_h("eyes/owlEye.h", "sclera", img_width=180, img_height=180,
                                 crop_width=160, crop_height=160)
if pixel_buffer:
    # Set address window for full 160x160 display and send pixel data.
    display.set_address_window(0, 0, 159, 159)
    display.send_pixels(pixel_buffer)
else:
    print("Failed to load image.")

input("Press Enter to exit...")
