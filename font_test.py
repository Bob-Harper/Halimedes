#!/usr/bin/env python3
import time
from eyes.dualeye_driver import eye_left, eye_right
from eyes.tools.text_draw import draw_text, draw_pixel
import json

from pathlib import Path

def load_font(path="eyes/tools/font_5x7_upright.json"):
    with open(path) as f:
        return json.load(f)

FONT_5X7 = load_font()

WIDTH, HEIGHT = 160, 160

def draw_checkerboard(eye, block=20):
    for y in range(HEIGHT):
        for x in range(WIDTH):
            color = 0xFFFF if ((x // block) + (y // block)) % 2 == 0 else 0x0000
            draw_pixel(eye, x, y, color)

def draw_test_text(eye):
    draw_text(eye, 30, 50, "HELLO", 0xF800, scale=2)
    draw_text(eye, 30, 80, "WORLD", 0x07E0, scale=2)

if __name__ == "__main__":
    for eye in (eye_right, eye_left, eye_right):
        eye.fill_screen(0x0000)
        draw_test_text(eye)
        time.sleep(5)
        eye.fill_screen(0x0000)
        draw_checkerboard(eye)
        time.sleep(5)
        eye.fill_screen(0x0000)
        time.sleep(5)

    print("Checkerboard + Text drawn to both eyes")

def draw_pixel(eye, x, y, color):
    if not (0 <= x < 160 and 0 <= y < 160):
        return  # Skip pixels outside display bounds
    eye.set_window(x, y, x, y)
    hi = (color >> 8) & 0xFF
    lo = color & 0xFF
    eye.write_data(bytes([hi, lo]))


def draw_char(eye, x, y, char, color, scale=1):
    char = char.upper()
    if char not in FONT_5X7:
        char = ' '
    pixels = FONT_5X7[char]
    for col, byte in enumerate(pixels):
        for row in range(7):
            if byte & (1 << row):
                for dx in range(scale):
                    for dy in range(scale):
                        draw_pixel(eye, x + col * scale + dx, y + row * scale + dy, color)

def draw_text(eye, x, y, text, color, scale=1, spacing=1):
    for i, char in enumerate(text):
        draw_char(eye, x + i * (5 * scale + spacing), y, char, color, scale)
