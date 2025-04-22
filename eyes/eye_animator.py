from PIL import Image
import time
import random
import numpy as np
from classes.dualeye_driver import eye_left, eye_right
from .eye_deform import EyeDeformer

class EyeAnimator:
    def __init__(self, profile):
        self.profile = profile
        self.image = profile.image
        self.deformer = EyeDeformer(
            sclera_size=profile.sclera_size,
            texture_name=profile.name
        )
        self.deformer.cache.warm_up_cache(kind="spherical", verbose=True)
        self.deformer.cache.warm_up_cache(kind="pupil", verbose=True)
        self.preload_eye_movements() 
        self.eyelids = {
            'top': profile.eyelid_top,
            'bottom': profile.eyelid_bottom,
            'left': profile.eyelid_left,
            'right': profile.eyelid_right,
        }
        self.current_x = 10
        self.current_y = 10
        self.current_pupil = 1.0
        self.gaze_buffers = {}
        self.width = self.height = 160

    def get_eye_region(self, x_off, y_off, base_img=None):
        base = base_img or self.image
        cropped = base.crop((x_off, y_off, x_off + self.width, y_off + self.height))
        buf = bytearray()
        for y in range(self.height):
            for x in range(self.width):
                r, g, b = cropped.getpixel((x, y))
                rgb = ((r & 0xF8) << 8) | ((g & 0xFC) << 3) | (b >> 3)
                buf.append((rgb >> 8) & 0xFF)
                buf.append(rgb & 0xFF)
        return buf

    def display_image_buffer(self, eye, buf):
        eye.set_window(0, 0, 159, 159)
        for i in range(0, len(buf), 1024):
            eye.write_data(buf[i:i+1024])

    def draw_gaze(self, x_off, y_off, pupil_size=1.0):
        key = (x_off, y_off, pupil_size)
        if key not in self.gaze_buffers:
            warped = self.deformer.generate_eye_frame(
                self.image,
                pupil_size=pupil_size,
                x_off=x_off,
                y_off=y_off,
                iris_radius=self.profile.iris_radius,
                feather_width=self.profile.feather_width,
                perspective_shift=self.profile.perspective_shift
            )

            eyelid_masked = self.apply_eyelids(warped)
            self.gaze_buffers[key] = self.get_eye_region(0, 0, base_img=eyelid_masked)
        buf = self.gaze_buffers[key]
        for eye in (eye_left, eye_right):
            self.display_image_buffer(eye, buf)

        self.current_x = x_off
        self.current_y = y_off
        self.current_pupil = pupil_size

    def apply_eyelids(self, img):
        arr = np.array(img)
        if self.eyelids['top'] > 0:
            arr[:self.eyelids['top'], :, :] = 0
        if self.eyelids['bottom'] > 0:
            arr[-self.eyelids['bottom']:, :, :] = 0
        if self.eyelids['left'] > 0:
            arr[:, :self.eyelids['left'], :] = 0
        if self.eyelids['right'] > 0:
            arr[:, -self.eyelids['right']:, :] = 0
        return Image.fromarray(arr)

    def blink(self, speed=0.02):
        self.dual_blink_cycle(
            pupil_size=self.current_pupil,
            x_off=self.current_x,
            y_off=self.current_y,
            close_speed=speed,
            open_speed=speed
        )

    def dual_blink_close(self, speed=0.02):
        for i in range(0, self.height // 2 + 1, 4):
            for eye in (eye_left, eye_right):
                eye.fill_rect(0, 0, self.width, i, 0x0000)
                eye.fill_rect(0, self.height - i, self.width, i, 0x0000)
            time.sleep(speed)
        for eye in (eye_left, eye_right):
            eye.fill_rect(0, self.height // 2 - 2, self.width, 4, 0x0000)

    def dual_blink_open(self, pupil_size=1.0, x_off=10, y_off=10, speed=0.02):
        warped = self.deformer.generate_eye_frame(
            self.image,
            pupil_size=pupil_size,
            x_off=x_off,
            y_off=y_off,
            iris_radius=self.profile.iris_radius,
            feather_width=self.profile.feather_width,
            perspective_shift=self.profile.perspective_shift
        )
        eyelid_masked = self.apply_eyelids(warped)

        rgb_buf = bytearray()
        for y in range(self.height):
            for x in range(self.width):
                r, g, b = eyelid_masked.getpixel((x, y))
                rgb = ((r & 0xF8) << 8) | ((g & 0xFC) << 3) | (b >> 3)
                rgb_buf.append((rgb >> 8) & 0xFF)
                rgb_buf.append(rgb & 0xFF)

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
                    chunk = rgb_buf[start:end]
                    for j in range(0, len(chunk), 1024):
                        eye.write_data(chunk[j:j + 1024])
            time.sleep(speed)

    def dual_blink_cycle(
        self,
        pupil_size=None,
        x_off=None,
        y_off=None,
        close_speed=0.02,
        open_speed=0.02,
        hold=0.1
    ):
        if pupil_size is None:
            pupil_size = self.current_pupil
        if x_off is None:
            x_off = self.current_x
        if y_off is None:
            y_off = self.current_y
            self.dual_blink_close(speed=close_speed)
        time.sleep(hold)
        self.dual_blink_open(pupil_size=pupil_size, x_off=x_off, y_off=y_off, speed=open_speed)

    def smooth_gaze_transition(self, from_x, from_y, to_x, to_y, from_pupil, to_pupil, steps=8, delay=0.015):
        for i in range(1, steps + 1):
            interp_x = int(from_x + (to_x - from_x) * (i / steps))
            interp_y = int(from_y + (to_y - from_y) * (i / steps))
            interp_pupil = from_pupil + (to_pupil - from_pupil) * (i / steps)
            self.draw_gaze(interp_x, interp_y, pupil_size=interp_pupil)
            time.sleep(delay)

    def smooth_gaze(self, to_x, to_y, to_pupil, steps=8, delay=0.015):
        self.smooth_gaze_transition(
            self.current_x, self.current_y,
            to_x, to_y,
            self.current_pupil, to_pupil,
            steps, delay
        )

    def apply_gaze_mode(self, mode):
        if mode == "left":
            self.smooth_gaze(5, 10, to_pupil=1.0)
        elif mode == "right":
            self.smooth_gaze(15, 10, to_pupil=1.0)
        elif mode == "up":
            self.smooth_gaze(10, 5, to_pupil=1.0)
        elif mode == "down":
            self.smooth_gaze(10, 15, to_pupil=1.0)
        elif mode == "center":
            self.smooth_gaze(10, 10, to_pupil=1.0)
        elif mode == "wander":
            self.smooth_gaze(random.randint(6, 14), random.randint(6, 14), to_pupil=random.uniform(0.95, 1.15))

    def set_expression(self, mood):
        # Map moods to eyelid shapes (you've already got access to those)
        expression_map = {
            "neutral": (32, 32, 0, 0),
            "happy": (12, 12, 0, 0),
            "sad": (20, 40, 0, 0),
            "angry": (10, 10, 4, 4),
            "surprised": (4, 4, 0, 0),
            "focused": (34, 34, 12, 12),
            "skeptical": (48, 16, 4, 0),
            "asleep": (0, 0, 0, 0),
        }
        top, bottom, left, right = expression_map.get(mood, (16, 16, 0, 0))
        self.set_eyelids(top, bottom, left, right)

    def set_eyelids(self, top, bottom, left, right):
        self.eyelids['top'] = top
        self.eyelids['bottom'] = bottom
        self.eyelids['left'] = left
        self.eyelids['right'] = right

        # Update the eye image with the new eyelid settings
        self.draw_gaze(self.current_x, self.current_y, pupil_size=self.current_pupil)

    def preload_eye_movements(self, pupil_steps=5, grid_step=2):
        print("[Boot] Preloading gaze/pupil deformation into cache...")
        for pupil in np.linspace(self.profile.pupil_min, self.profile.pupil_max, pupil_steps):
            for x in range(0, 21, grid_step):
                for y in range(0, 21, grid_step):
                    _ = self.deformer.generate_eye_frame(
                        self.image,
                        pupil_size=pupil,
                        x_off=x,
                        y_off=y,
                        iris_radius=self.profile.iris_radius,
                        feather_width=self.profile.feather_width,
                        perspective_shift=self.profile.perspective_shift
                    )
        print("[Boot] Preload complete.")

