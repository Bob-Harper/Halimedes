#!/usr/bin/env python3
import time, math
from dualeye_driver2 import eye_left, eye_right
from helpers.text_draw import draw_text, draw_pixel
from PIL import Image

WIDTH, HEIGHT = 160, 160


def test_text1():
    eye_left.fill_screen(0x0000)
    draw_text(eye_left, 20, 40, "HELLO!", 0xF800, scale=3)
    draw_text(eye_left, 20, 70, "HALIMEDES", 0x07E0, scale=3)
    draw_text(eye_left, 20, 100, "ONLINE.", 0x001F, scale=3)

def test_text2():
    eye_right.fill_screen(0x0000)
    draw_text(eye_right, 20, 40, "GOOD", 0xF800, scale=3)
    draw_text(eye_right, 20, 70, "MORNING", 0x07E0, scale=3)
    draw_text(eye_right, 20, 100, "ONNALYN!", 0x001F, scale=3)


def draw_pixels(eye, xy_color_list):
    for x, y, color in xy_color_list:
        draw_pixel(eye, x, y, color)

def fill_rect(eye, x, y, w, h, color):
    eye.set_window(x, y, x + w - 1, y + h - 1)
    hi = (color >> 8) & 0xFF
    lo = color & 0xFF
    buf = bytes([hi, lo]) * (w * h)
    for i in range(0, len(buf), 4096):
        eye.write_data(buf[i:i+4096])

def draw_circle(eye, cx, cy, r, color):
    for y in range(-r, r + 1):
        for x in range(-r, r + 1):
            if x*x + y*y <= r*r:
                draw_pixel(eye, cx + x, cy + y, color)

def draw_checkerboard(eye, block=20):
    for y in range(HEIGHT):
        for x in range(WIDTH):
            if ((x // block) + (y // block)) % 2 == 0:
                color = 0xFFFF
            else:
                color = 0x0000
            draw_pixel(eye, x, y, color)

def draw_concentric_rings(eye):
    cx, cy = WIDTH // 2, HEIGHT // 2
    for y in range(HEIGHT):
        for x in range(WIDTH):
            dist = int(math.hypot(x - cx, y - cy)) // 10
            color = 0xFFFF if dist % 2 == 0 else 0x0000
            draw_pixel(eye, x, y, color)

def draw_time(hhmmss, color=0xF800):
    eye_left.fill_screen(0x0000)
    draw_text(eye_left, 18, 72, hhmmss, color, scale=3)

def draw_date(color=0xF800):
    eye_right.fill_screen(0x0000)
    date = time.strftime("%d %b %Y").upper()
    draw_text(eye_right, 10, 72, date, color, scale=3)

def format_time():
    return time.strftime("%H:%M:%S")

def narrate(lines, color=0xF800, delay=2.0):
    for eye in (eye_left, eye_right):
        eye.fill_screen(0x0000)
        for i, line in enumerate(lines):
            draw_text(eye, 10, 40 + (i * 20), line, color, scale=2)
    print(" >>", " ".join(lines))
    time.sleep(delay)

def display_image_file(path):
    img = Image.open(path).convert('RGB')
    img = img.resize((160, 160))

    rgb565_bytes = []
    for y in range(160):
        for x in range(160):
            r, g, b = img.getpixel((x, y))
            rgb = ((r & 0xF8) << 8) | ((g & 0xFC) << 3) | (b >> 3)
            rgb565_bytes.append((rgb >> 8) & 0xFF)
            rgb565_bytes.append(rgb & 0xFF)

    buf = bytes(rgb565_bytes)
    for eye in (eye_left, eye_right):
        eye.set_window(0, 0, 159, 159)
        for i in range(0, len(buf), 1024):
            eye.write_data(buf[i:i+1024])

def run_clock():
    print("Halimedes is now a timekeeper.")
    while True:
        now = format_time()
        draw_time(now)
        draw_date()
        time.sleep(1)

if __name__ == "__main__":
    narrate(["Filling screen", "with black"])
    eye_left.fill_screen(0x0000)
    eye_right.fill_screen(0x0000)
    time.sleep(0.5)

    # Test solid fills
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
        for eye in (eye_left, eye_right):
            eye.fill_screen(color)
        time.sleep(1)

    narrate(["Checkerboard +", "Rings"])
    for eye in (eye_left, eye_right):
        eye.fill_screen(0x0000)
    draw_checkerboard(eye_right)
    draw_concentric_rings(eye_left)
    time.sleep(2)

    narrate(["Drawing circle", "(red)"])
    eye_left.fill_screen(0x0000)
    draw_circle(eye_left, 80, 80, 30, 0xF800)
    time.sleep(2)

    narrate(["Rectangle", "(green)"])
    eye_right.fill_screen(0x0000)
    fill_rect(eye_right, 30, 30, 100, 50, 0x07E0)
    time.sleep(2)

    narrate(["Pixel center", "(blue)"])
    for eye in (eye_left, eye_right):
        eye.fill_screen(0x0000)
        draw_pixel(eye, 80, 80, 0x001F)
    time.sleep(2)

    narrate(["Drawing text"])
    for eye in (eye_left, eye_right):
        eye.fill_screen(0x0000)
    test_text1()
    test_text2()
    time.sleep(8)

    narrate(["Staring contest!", "(DON'T BLINK)"])
    for eye in (eye_left, eye_right):
        eye.fill_screen(0x0000)
        display_image_file("/home/msutt/hal/eyes/blueye.png")
    time.sleep(20)
   
    narrate(["Render complete", "Clock time!"])
    run_clock()
