from gc9d01_library import GC9D01
import board
import busio
import digitalio
import time
import math

# Import the font directly in your script
from gc9d01_library.font5x7 import FONT_5X7

# Setup SPI communication
spi = busio.SPI(clock=board.SCK, MOSI=board.MOSI)
spi.try_lock()
spi.configure(baudrate=24000000, phase=0, polarity=0)
spi.unlock()

# Setup control pins
cs = digitalio.DigitalInOut(board.CE0)  # Chip Select
dc = digitalio.DigitalInOut(board.D25)  # Data/Command
rst = digitalio.DigitalInOut(board.D24)  # Reset

# Create display object
display = GC9D01(spi, dc, cs, rst)
time.sleep(0.1)  # Short delay after initialization

# Create a buffer for the clock face
buffer_size = 160 * 160
clock_face_buffer = bytearray(buffer_size * 2)  # 2 bytes per pixel for 16-bit color

def fill_buffer(buffer, color):
    color_bytes = color.to_bytes(2, 'big')
    for i in range(0, len(buffer), 2):
        buffer[i:i+2] = color_bytes

def draw_pixel_buffer(buffer, x, y, color):
    if 0 <= x < 160 and 0 <= y < 160:
        index = (y * 160 + x) * 2
        buffer[index:index+2] = color.to_bytes(2, 'big')

def draw_circle_buffer(buffer, x0, y0, r, color):
    f = 1 - r
    ddF_x = 1
    ddF_y = -2 * r
    x = 0
    y = r

    draw_pixel_buffer(buffer, x0, y0 + r, color)
    draw_pixel_buffer(buffer, x0, y0 - r, color)
    draw_pixel_buffer(buffer, x0 + r, y0, color)
    draw_pixel_buffer(buffer, x0 - r, y0, color)

    while x < y:
        if f >= 0:
            y -= 1
            ddF_y += 2
            f += ddF_y
        x += 1
        ddF_x += 2
        f += ddF_x

        draw_pixel_buffer(buffer, x0 + x, y0 + y, color)
        draw_pixel_buffer(buffer, x0 - x, y0 + y, color)
        draw_pixel_buffer(buffer, x0 + x, y0 - y, color)
        draw_pixel_buffer(buffer, x0 - x, y0 - y, color)
        draw_pixel_buffer(buffer, x0 + y, y0 + x, color)
        draw_pixel_buffer(buffer, x0 - y, y0 + x, color)
        draw_pixel_buffer(buffer, x0 + y, y0 - x, color)
        draw_pixel_buffer(buffer, x0 - y, y0 - x, color)

def draw_line_buffer(buffer, x0, y0, x1, y1, color):
    dx = abs(x1 - x0)
    dy = abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx - dy

    while True:
        draw_pixel_buffer(buffer, x0, y0, color)
        if x0 == x1 and y0 == y1:
            break
        e2 = 2 * err
        if e2 > -dy:
            err -= dy
            x0 += sx
        if e2 < dx:
            err += dx
            y0 += sy

def create_clock_face():
    fill_buffer(clock_face_buffer, 0x0000)  # Black background
    center_x, center_y = 79, 79
    radius = 75

    # Draw clock circle
    draw_circle_buffer(clock_face_buffer, center_x, center_y, radius, 0xFFFF)  # White circle

    # Draw hour markers
    for hour in range(12):
        angle = math.radians(hour * 30 - 90)
        outer_x = int(center_x + radius * math.cos(angle))
        outer_y = int(center_y + radius * math.sin(angle))
        inner_x = int(center_x + (radius - 10) * math.cos(angle))
        inner_y = int(center_y + (radius - 10) * math.sin(angle))
        draw_line_buffer(clock_face_buffer, outer_x, outer_y, inner_x, inner_y, 0xFFFF)

def draw_hand(buffer, angle, length, color):
    center_x, center_y = 79, 79
    end_x = int(center_x + length * math.cos(math.radians(angle - 90)))
    end_y = int(center_y + length * math.sin(math.radians(angle - 90)))
    draw_line_buffer(buffer, center_x, center_y, end_x, end_y, color)

def update_clock(display):
    global last_minute
    
    # Create a copy of the clock face buffer
    update_buffer = bytearray(clock_face_buffer)
    
    # Get current time
    current_time = time.localtime()
    hours = current_time.tm_hour % 12
    minutes = current_time.tm_min
    seconds = current_time.tm_sec

    # Calculate hand angles
    hour_angle = (hours + minutes / 60) * 30
    minute_angle = minutes * 6
    second_angle = seconds * 6

    # Draw hands
    draw_hand(update_buffer, hour_angle, 40, 0xF800)  # Red hour hand
    draw_hand(update_buffer, minute_angle, 55, 0x07E0)  # Green minute hand
    draw_hand(update_buffer, second_angle, 60, 0x001F)  # Blue second hand

    # Draw center dot
    draw_circle_buffer(update_buffer, 79, 79, 3, 0xFFFF)

    # Update display
    display.set_window(0, 0, 159, 159)
    display.write_data(update_buffer)

    # Update text only when minute changes
    if minutes != last_minute:
        last_minute = minutes
        hours = hours if hours != 0 else 12  # Convert 0 to 12 for display
        time_str = f"{hours:2d}:{minutes:02d}"
        text_width = len(time_str) * 6 * 2  # 6 pixels per character, scale of 2
        text_x = (display.width - text_width) // 2
        
        # Clear previous text area
        for y in range(100, 114):  # Adjust these values based on your text size and position
            for x in range(text_x, text_x + text_width):
                display.draw_pixel(x, y, 0x0000)  # Black color to clear
        
        # Draw new text
        draw_text(display, text_x, 100, time_str, 0xFFFF, scale=2)  # White text, scaled up, centered

# Add these methods to your script
def draw_char(display, x, y, char, color, scale=1):
    if char not in FONT_5X7:
        return
    for row in range(7):
        for col in range(5):
            if FONT_5X7[char][col] & (1 << row):  # Changed back to original column order and flipped row
                for i in range(scale):
                    for j in range(scale):
                        display.draw_pixel(x + col * scale + i, y + row * scale + j, color)

def draw_text(display, x, y, text, color, scale=1):
    for i, char in enumerate (reversed(text)):  # Changed from enumerate(text)
        draw_char(display, x + (len(text) - 1 - i) * 6 * scale, y, char.upper(), color, scale)

# Initialize the clock face
create_clock_face()

# Add this after your imports
last_minute = -1  # Initialize to an impossible value

# Main loop
while True:
    update_clock(display)
    time.sleep(1)
