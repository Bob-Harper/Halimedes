import time
from dualeye_driver2 import eye_left, eye_right
from PIL import Image

WIDTH = HEIGHT = 160
EYEBALL_IMAGE = "/home/msutt/hal/eyes/blueye.png"
BLINK_INTERVAL = 5  # seconds


def load_eyeball_image(path):
    img = Image.open(path).convert('RGB').resize((160, 160))
    buf = bytearray()
    for y in range(160):
        for x in range(160):
            r, g, b = img.getpixel((x, y))
            rgb = ((r & 0xF8) << 8) | ((g & 0xFC) << 3) | (b >> 3)
            buf.append((rgb >> 8) & 0xFF)
            buf.append(rgb & 0xFF)
    return buf


def dual_blink_close(speed=0.02):
    for i in range(0, HEIGHT // 2 + 1, 4):
        for eye in (eye_left, eye_right):
            eye.fill_rect(0, 0, WIDTH, i, 0x0000)
            eye.fill_rect(0, HEIGHT - i, WIDTH, i, 0x0000)
        time.sleep(speed)
    
    # Final absolute blackout to guarantee closure
    for eye in (eye_left, eye_right):
        eye.fill_rect(0, HEIGHT // 2 - 2, WIDTH, 4, 0x0000)  # 4-pixel patch

def dual_blink_open(eyeball_buf, speed=0.02):
    for eye in (eye_left, eye_right):
        eye.fill_screen(0x0000)

    for i in range(HEIGHT // 2, -1, -4):
        y0 = i
        y1 = HEIGHT - i - 1
        if y1 < y0:
            continue  # Skip invalid windows

        for eye in (eye_left, eye_right):
            eye.set_window(0, y0, WIDTH - 1, y1)

            for row in range(y0, y1 + 1):  # Inclusive
                start = row * WIDTH * 2
                end = start + WIDTH * 2
                chunk = eyeball_buf[start:end]
                for j in range(0, len(chunk), 1024):
                    eye.write_data(chunk[j:j+1024])

        time.sleep(speed)


def dual_blink_cycle(eyeball_buf, close_speed=0.02, open_speed=0.02, hold=0.1):
    dual_blink_close(speed=close_speed)
    time.sleep(hold)
    dual_blink_open(eyeball_buf, speed=open_speed)


def main():
    eyeball_buf = load_eyeball_image(EYEBALL_IMAGE)

    # Start with screen off
    for eye in (eye_left, eye_right):
        eye.fill_screen(0x0000)
    time.sleep(2)

    # Dramatic wake-up
    dual_blink_open(eyeball_buf, speed=0.08)
    time.sleep(2)
    for _ in range(3):
        dual_blink_cycle(eyeball_buf, close_speed=0.01, open_speed=0.0001, hold=0.1)
        time.sleep(BLINK_INTERVAL)

    print("Okay I'm awake now... where's my coffee?  No coffee?  Goodnight.")
    time.sleep(2)
    dual_blink_close(speed=0.05)


if __name__ == "__main__":
    import select
    main()
