#!/usr/bin/env python3
import time
import math
import datetime
from PIL import Image, ImageDraw
from dualeye import GC9D01Display

def pil_to_rgb565_bytearray(img):
    """
    Converts a PIL Image (mode "RGB") to a bytearray containing RGB565 data (big-endian).
    """
    pixel_data = list(img.getdata())
    buf = bytearray()
    for (r, g, b) in pixel_data:
        # Convert 8-bit per channel to 5-6-5 format:
        r5 = r >> 3
        g6 = g >> 2
        b5 = b >> 3
        color = (r5 << 11) | (g6 << 5) | b5
        buf.append((color >> 8) & 0xFF)
        buf.append(color & 0xFF)
    return buf

# Initialize the display (adjust GPIO pins as needed)
display = GC9D01Display(cs_pin=6, dc_pin=13, rst_pin=24, bl_pin=None)
display.reset()
display.init_display()

# Display dimensions and clock face parameters
width, height = 160, 160
center = (width // 2, height // 2)
radius = 75

while True:
    # Create a new image with a black background
    img = Image.new("RGB", (width, height), "black")
    draw = ImageDraw.Draw(img)

    # Draw the outer circle of the clock face
    draw.ellipse((center[0]-radius, center[1]-radius, center[0]+radius, center[1]+radius), outline="white", width=2)

    # Draw tick marks at each hour (every 30 degrees)
    for angle in range(0, 360, 30):
        rad = math.radians(angle)
        x_outer = center[0] + radius * math.cos(rad)
        y_outer = center[1] + radius * math.sin(rad)
        tick_length = 10
        x_inner = center[0] + (radius - tick_length) * math.cos(rad)
        y_inner = center[1] + (radius - tick_length) * math.sin(rad)
        draw.line((x_outer, y_outer, x_inner, y_inner), fill="white", width=2)

    # Get current time
    now = datetime.datetime.now()
    second = now.second + now.microsecond / 1e6
    minute = now.minute + second / 60.0
    hour = (now.hour % 12) + minute / 60.0

    # Calculate angles for each hand (adjusting so that 0° is at the top)
    second_angle = math.radians(second * 6 - 90)  # 6° per second
    minute_angle = math.radians(minute * 6 - 90)   # 6° per minute
    hour_angle = math.radians(hour * 30 - 90)        # 30° per hour

    # Define hand lengths
    second_length = radius - 10
    minute_length = radius - 20
    hour_length = radius - 35

    # Draw the second hand (red, thin)
    sec_end = (center[0] + second_length * math.cos(second_angle),
               center[1] + second_length * math.sin(second_angle))
    draw.line((center[0], center[1], sec_end[0], sec_end[1]), fill="red", width=1)

    # Draw the minute hand (white, medium thickness)
    min_end = (center[0] + minute_length * math.cos(minute_angle),
               center[1] + minute_length * math.sin(minute_angle))
    draw.line((center[0], center[1], min_end[0], min_end[1]), fill="white", width=3)

    # Draw the hour hand (white, thick)
    hr_end = (center[0] + hour_length * math.cos(hour_angle),
              center[1] + hour_length * math.sin(hour_angle))
    draw.line((center[0], center[1], hr_end[0], hr_end[1]), fill="white", width=5)

    # Optionally, draw a small circle at the center
    draw.ellipse((center[0]-3, center[1]-3, center[0]+3, center[1]+3), fill="white")

    # Convert the PIL image to an RGB565 bytearray
    pixel_buffer = pil_to_rgb565_bytearray(img)
    # Set the address window to cover the entire display and send pixel data
    display.set_address_window(0, 0, width - 1, height - 1)
    display.send_pixels(pixel_buffer)

    # Update the clock every half second
    time.sleep(0.5)
