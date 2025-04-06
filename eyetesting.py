#!/usr/bin/env python3
import time
from dualeye import GC9D01Display, fill_screen_color, draw_color_stripes

# Instantiate the display (adjust GPIO pin numbers as needed):
display = GC9D01Display(cs_pin=6, dc_pin=13, rst_pin=24, bl_pin=None)
display.reset()
display.init_display()

""" # Prepare a gradient buffer (black->white horizontal gradient)
width = 160
height = 160
pixel_buffer = bytearray()
for y in range(height):
    for x in range(width):
        # Compute brightness from 0 to 31 (for R/B) and 0 to 63 (for G) based on x
        level5 = (x * 31) // (width - 1)    # 5-bit value (0-31)
        level6 = (x * 63) // (width - 1)    # 6-bit value (0-63)
        # Construct 16-bit RGB565: 5-bit R, 6-bit G, 5-bit B
        color = (level5 << 11) | (level6 << 5) | (level5)
        # Append high byte then low byte
        pixel_buffer.append((color >> 8) & 0xFF)
        pixel_buffer.append(color & 0xFF)

# Set the draw area to entire screen and send pixel data
display.set_address_window(0, 0, width - 1, height - 1)
display.send_pixels(pixel_buffer)
time.sleep(5) """

# Now test solid color fills:
fill_screen_color(display, 0xF800)  # Red
time.sleep(1)
fill_screen_color(display, 0x07E0)  # Green
time.sleep(1)
fill_screen_color(display, 0x001F)  # Blue
time.sleep(1)
fill_screen_color(display, 0xFFE0)  # Yellow
time.sleep(1)
fill_screen_color(display, 0x07FF)  # Cyan
time.sleep(1)
fill_screen_color(display, 0xF81F)  # Magenta
time.sleep(1)

# Finally, test drawing color stripes
# draw_color_stripes(display)
# time.sleep(1)

input("Press Enter to exit...")
