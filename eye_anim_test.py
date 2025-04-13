import time
from classes.dualeye_driver import eye_left, eye_right
from helpers.eye_loader import load_eye_profile
from PIL import Image
import numpy as np
import random

profile = load_eye_profile("180blue")  # or whatever .json name you're using
full_img = profile.image
SCLERA_SIZE = profile.sclera_radius
SOURCE_SIZE = 180  # Always convert eye textures to this pixel size
WIDTH = HEIGHT = 160
# Pre-rendered gaze positions (centered, left, right, up, down)
gaze_buffers = {}


def get_eye_region(x_off, y_off, base_img=None):
    if base_img is None:
        base_img = full_img  # fallback to default
    cropped = base_img.crop((x_off, y_off, x_off + WIDTH, y_off + HEIGHT))
    buf = bytearray()
    for y in range(HEIGHT):
        for x in range(WIDTH):
            r, g, b = cropped.getpixel((x, y))
            rgb = ((r & 0xF8) << 8) | ((g & 0xFC) << 3) | (b >> 3)
            buf.append((rgb >> 8) & 0xFF)
            buf.append(rgb & 0xFF)
    return buf


def display_image_buffer(eye, buf):
    eye.set_window(0, 0, 159, 159)
    for i in range(0, len(buf), 1024):
        eye.write_data(buf[i:i+1024])


def draw_gaze(x_off, y_off, pupil_size=1.0):
    key = (x_off, y_off, pupil_size)
    if key not in gaze_buffers:
        warped = warp_pupil(full_img, pupil_size, x_off=x_off, y_off=y_off)
        eyelids_applied = apply_eyelids(warped, top=32, bottom=32, left=0, right=0)
        # Pre-render the gaze position
        gaze_buffers[key] = get_eye_region(0, 0, base_img=eyelids_applied)
    buf = gaze_buffers[key]
    for eye in (eye_left, eye_right):
        display_image_buffer(eye, buf)


def dual_blink_close(speed=0.02):
    for i in range(0, HEIGHT // 2 + 1, 4):
        for eye in (eye_left, eye_right):
            eye.fill_rect(0, 0, WIDTH, i, 0x0000)
            eye.fill_rect(0, HEIGHT - i, WIDTH, i, 0x0000)
        time.sleep(speed)
    for eye in (eye_left, eye_right):
        eye.fill_rect(0, HEIGHT // 2 - 2, WIDTH, 4, 0x0000)


def dual_blink_open(source_image, pupil_size=1.0, speed=0.02):
    warped = warp_pupil(source_image, pupil_size)
    eyelids_applied = apply_eyelids(warped, top=32, bottom=32, left=0, right=0)
    rgb_buf = bytearray()
    for y in range(160):
        for x in range(160):
            r, g, b = eyelids_applied.getpixel((x, y))
            rgb = ((r & 0xF8) << 8) | ((g & 0xFC) << 3) | (b >> 3)
            rgb_buf.append((rgb >> 8) & 0xFF)
            rgb_buf.append(rgb & 0xFF)

    for eye in (eye_left, eye_right):
        eye.fill_screen(0x0000)

    for i in range(HEIGHT // 2, -1, -4):
        y0 = i
        y1 = HEIGHT - i - 1
        if y1 < y0:
            continue

        for eye in (eye_left, eye_right):
            eye.set_window(0, y0, WIDTH - 1, y1)
            for row in range(y0, y1 + 1):
                start = row * WIDTH * 2
                end = start + WIDTH * 2
                chunk = rgb_buf[start:end]
                for j in range(0, len(chunk), 1024):
                    eye.write_data(chunk[j:j + 1024])
        time.sleep(speed)


def dual_blink_cycle(source_image, pupil_size=1.0, close_speed=0.02, open_speed=0.02, hold=0.1):
    dual_blink_close(speed=close_speed)
    time.sleep(hold)
    dual_blink_open(source_image, pupil_size=pupil_size, speed=open_speed)


def warp_pupil(source_img, pupil_size=1.0, output_size=160, x_off=10, y_off=10):
    dilation = 1.0 / pupil_size
    assert source_img.size == (180, 180), "Expected 180x180 base image"

    # Instead of fixed center, base it on gaze
    center_x = 90 + (x_off - 10)  # Moves center from 80→100
    center_y = 90 + (y_off - 10)

    output = np.zeros((output_size, output_size, 3), dtype=np.uint8)
    yy, xx = np.meshgrid(np.arange(output_size), np.arange(output_size), indexing='xy')
    norm_x = (xx - output_size // 2) / (output_size // 2)
    norm_y = (yy - output_size // 2) / (output_size // 2)
    radius = np.sqrt(norm_x**2 + norm_y**2)
    angle = np.arctan2(norm_y, norm_x)

    warped_radius = radius ** dilation
    warped_radius = np.clip(warped_radius, 0.0, 1.0)

    # Map to 180x180 full image coordinates
    sample_x = warped_radius * np.cos(angle) * SCLERA_SIZE + center_x
    sample_y = warped_radius * np.sin(angle) * SCLERA_SIZE + center_y

    source_pixels = np.array(source_img)
    h, w = source_pixels.shape[:2]
    x0 = np.floor(sample_x).astype(np.int32)
    y0 = np.floor(sample_y).astype(np.int32)
    x1 = np.clip(x0 + 1, 0, w - 1)
    y1 = np.clip(y0 + 1, 0, h - 1)
    x0 = np.clip(x0, 0, w - 1)
    y0 = np.clip(y0, 0, h - 1)

    wa = (x1 - sample_x) * (y1 - sample_y)
    wb = (sample_x - x0) * (y1 - sample_y)
    wc = (x1 - sample_x) * (sample_y - y0)
    wd = (sample_x - x0) * (sample_y - y0)

    for c in range(3):
        a = source_pixels[y0, x0, c]
        b = source_pixels[y0, x1, c]
        c_ = source_pixels[y1, x0, c]
        d = source_pixels[y1, x1, c]
        output[..., c] = (
            wa * a + wb * b + wc * c_ + wd * d
        ).astype(np.uint8)

    return Image.fromarray(output)

def apply_eyelids(img, top=0, bottom=0, left=0, right=0):
    """
    Apply black overlay as eyelids around any side of the image.
    Each value is in pixels. You can specify top, bottom, left, and right independently.
    """
    arr = np.array(img)

    if top > 0:
        arr[:top, :, :] = 0
    if bottom > 0:
        arr[-bottom:, :, :] = 0
    if left > 0:
        arr[:, :left, :] = 0
    if right > 0:
        arr[:, -right:, :] = 0

    return Image.fromarray(arr)

def smooth_gaze_transition(from_x, from_y, to_x, to_y, from_pupil, to_pupil, steps=6, delay=0.02):
    """
    Smoothly animate gaze and pupil size from current to target.
    """
    for i in range(1, steps + 1):
        interp_x = int(from_x + (to_x - from_x) * (i / steps))
        interp_y = int(from_y + (to_y - from_y) * (i / steps))
        interp_pupil = from_pupil + (to_pupil - from_pupil) * (i / steps)
        draw_gaze(interp_x, interp_y, pupil_size=interp_pupil)
        time.sleep(delay)


def main():
    # Eyes start off
    for eye in (eye_left, eye_right):
        eye.fill_screen(0x0000)
    time.sleep(1)

    # Dramatic slow wake-up with dilated pupil
    print("Booting up...")
    dual_blink_open(full_img, pupil_size=1.5, speed=0.08)
    time.sleep(1)

    # Blink a few times to adjust
    for _ in range(2):
        dual_blink_cycle(full_img, pupil_size=0.6, close_speed=0.01, open_speed=0.025)
        time.sleep(1)

    print("Entering idle gaze mode...")
    dual_blink_cycle(full_img, pupil_size=1.0, close_speed=0.01, open_speed=0.01)

    # Define gaze positions (avoiding edges if needed)
    gaze_coords = [(x, y) for x in (0, 10, 20) for y in (0, 10, 20)]
    current_x, current_y = 10, 10  # start centered
    current_pupil = 1.0            # initial pupil size
    try:
        while True:
            new_x, new_y = random.choice(gaze_coords)
            pupil = random.uniform(0.8, 1.4)
            smooth_gaze_transition(current_x, current_y, new_x, new_y, current_pupil, pupil)
            current_x, current_y = new_x, new_y
            current_pupil = pupil
            time.sleep(random.uniform(0.4, 1.3))

            # Occasionally blink
            if random.random() < 0.15:
                dual_blink_cycle(full_img, pupil_size=pupil, close_speed=0.015, open_speed=0.03, hold=0.05)

    except KeyboardInterrupt:
        print("\nNo coffee? ... shutting down.")
        dual_blink_cycle(full_img, pupil_size=1.2, close_speed=0.04, open_speed=0.06)
        time.sleep(0.5)
        dual_blink_close(speed=0.1)


if __name__ == "__main__":
    main()
