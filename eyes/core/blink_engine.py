import time
from eyes.dualeye_driver import eye_left, eye_right
from .draw_engine import DrawEngine

class BlinkEngine:
    def __init__(self, drawer: DrawEngine):
        self.drawer = drawer
        self.width = 160
        self.height = 160

    def dual_blink_close(self, speed=0.02):
        for i in range(0, self.height // 2 + 1, 4):
            for eye in (eye_left, eye_right):
                eye.fill_rect(0, 0, self.width, i, 0x0000)
                eye.fill_rect(0, self.height - i, self.width, i, 0x0000)
            time.sleep(speed)
        for eye in (eye_left, eye_right):
            eye.fill_rect(0, self.height // 2 - 2, self.width, 4, 0x0000)

    def dual_blink_open(self, buf, speed=0.02):
        for eye in (eye_left, eye_right):
            eye.fill_screen(0x0000)

        for i in range(self.height // 2, -1, -4):
            y0 = i
            y1 = self.height - i - 1
            if y1 < y0:
                continue
            for eye in (eye_left, eye_right):
                eye.set_window(0, y0, self.width - 1, y1)
                for row in range(y0, y1 + 1):
                    start = row * self.width * 2
                    end = start + self.width * 2
                    chunk = buf[start:end]
                    for j in range(0, len(chunk), 1024):
                        eye.write_data(chunk[j:j + 1024])
            time.sleep(speed)

    def blink(self, buf, close_speed=0.02, open_speed=0.02, hold=0.1):
        self.dual_blink_close(speed=close_speed)
        time.sleep(hold)
        self.dual_blink_open(buf, speed=open_speed)
