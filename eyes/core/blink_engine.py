from typing import Protocol, Union, Tuple
import random, asyncio
from eyes.dualeye_driver import eye_left, eye_right

class AnimatorWithBuffer(Protocol):
    """Animator just needs to expose .last_buf, which may be a single buf or a (left,right) tuple."""
    last_buf: Union[bytearray, Tuple[bytearray, bytearray]]

class BlinkEngine:
    def __init__(self, animator: AnimatorWithBuffer) -> None:
        self.animator = animator
        self.width    = 160
        self.height   = 160

    async def blink_sequence(self, base_buf: Union[bytearray, Tuple[bytearray, bytearray]], 
                             close_speed=0.02, open_speed=0.02, hold=0.1):
        """Yields progressive blink frames from current base buffer, coroutine style."""
        async with self.shared_lock:
            # Close phase
            for i in range(0, self.height // 2 + 1, 4):
                yield self._apply_blink_mask(base_buf, i)
                await asyncio.sleep(close_speed)

            # Hold closed
            yield self._apply_blink_mask(base_buf, self.height // 2)
            await asyncio.sleep(hold)

            # Open phase
            for i in range(self.height // 2, -1, -4):
                yield self._apply_blink_mask(base_buf, i)
                await asyncio.sleep(open_speed)


    def _apply_blink_mask(self, buf: Union[bytearray, Tuple[bytearray, bytearray]], i: int):
        """Returns a copy of the buffer with top/bottom black bars simulating eyelid closure."""
        if isinstance(buf, tuple):
            left_buf, right_buf = buf
        else:
            left_buf = right_buf = buf

        def mask_eye(original: bytearray) -> bytearray:
            new_buf = bytearray(original)
            for y in range(i):
                row_start = y * self.width * 2
                row_end = row_start + self.width * 2
                new_buf[row_start:row_end] = b'\x00' * (self.width * 2)

                yb = self.height - 1 - y
                row_start_b = yb * self.width * 2
                row_end_b = row_start_b + self.width * 2
                new_buf[row_start_b:row_end_b] = b'\x00' * (self.width * 2)

            return new_buf

        return (mask_eye(left_buf), mask_eye(right_buf))

    # The following may be deprecated/obsolete with the new sequencing system.
    # This is the blink call.  It should be only be called by idle_blink_loop. 
    # Other usage calls should rare and only come from an override manager class.
"""     def blink(self, buf: Union[bytearray, Tuple[bytearray, bytearray]],
                    close_speed=0.02, open_speed=0.02, hold=0.1):
        self.dual_blink_close(speed=close_speed)
        time.sleep(hold)
        self.dual_blink_open(buf, speed=open_speed)

    # This is the dual blink close.  It should never be called by anything but blink()
    def dual_blink_close(self, speed=0.02): 
        for i in range(0, self.height//2 + 1, 4):
            for eye in (eye_left, eye_right):
                eye.fill_rect(0, 0, self.width, i, 0x0000)
                eye.fill_rect(0, self.height - i, self.width, i, 0x0000)
            time.sleep(speed)
        # final little overlap to seal
        for eye in (eye_left, eye_right):
            eye.fill_rect(0, self.height//2 - 2, self.width, 4, 0x0000)

    # This is the dual blink open.  It should never be called by anything but blink()
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
            
    # This is the autonomous background blinking loop
    async def idle_blink_loop(self):  
        while True:
            await asyncio.sleep(random.uniform(4, 10))
            buf = self.animator.last_buf
            if buf:
                self.blink(buf)
 """