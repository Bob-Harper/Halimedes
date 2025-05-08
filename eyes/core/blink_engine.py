from typing import Protocol, Union, Tuple
import time, random, asyncio
from eyes.dualeye_driver import eye_left, eye_right

class AnimatorWithBuffer(Protocol):
    """Animator just needs to expose .last_buf, which may be a single buf or a (left,right) tuple."""
    last_buf: Union[bytearray, Tuple[bytearray, bytearray]]

class BlinkEngine:
    def __init__(self, animator: AnimatorWithBuffer) -> None:
        self.animator = animator
        self.width    = 160
        self.height   = 160

    async def idle_blink_loop(self):
        while True:
            await asyncio.sleep(random.uniform(4, 10))
            buf = self.animator.last_buf
            if buf:
                self.blink(buf)

    def dual_blink_close(self, speed=0.02):
        for i in range(0, self.height//2 + 1, 4):
            for eye in (eye_left, eye_right):
                eye.fill_rect(0, 0, self.width, i, 0x0000)
                eye.fill_rect(0, self.height - i, self.width, i, 0x0000)
            time.sleep(speed)
        # final little overlap to seal
        for eye in (eye_left, eye_right):
            eye.fill_rect(0, self.height//2 - 2, self.width, 4, 0x0000)

    def dual_blink_open(self, buf: Union[bytearray, Tuple[bytearray, bytearray]], speed=0.02):
        # clear screens
        for eye in (eye_left, eye_right):
            eye.fill_screen(0x0000)

        # split into left/right if needed
        if isinstance(buf, tuple):
            left_buf, right_buf = buf
        else:
            left_buf = right_buf = buf

        # reveal line by line
        for i in range(self.height // 2, -1, -4):
            y0, y1 = i, self.height - i - 1
            if y1 < y0:
                continue

            start = y0 * self.width * 2
            end   = (y1 + 1) * self.width * 2

            # Left eye
            eye_left.set_window(0, y0, self.width - 1, y1)
            segment = left_buf[start:end]
            for offset in range(0, len(segment), 1024):
                eye_left.write_data(segment[offset:offset+1024])

            # Right eye
            eye_right.set_window(0, y0, self.width - 1, y1)
            segment = right_buf[start:end]
            for offset in range(0, len(segment), 1024):
                eye_right.write_data(segment[offset:offset+1024])

            time.sleep(speed)
            
    def blink(self, buf: Union[bytearray, Tuple[bytearray, bytearray]],
                    close_speed=0.02, open_speed=0.02, hold=0.1):
        self.dual_blink_close(speed=close_speed)
        time.sleep(hold)
        self.dual_blink_open(buf, speed=open_speed)
