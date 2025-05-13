from eyes.dualeye_driver import eye_left, eye_right
from .eyelid_masker import apply_eyelids
from .eyelid_controller import EyelidController
from .eye_deform import EyeDeformer
from PIL import Image
import numpy as np


class DrawEngine:
    def __init__(self, profile):
        self.profile = profile
        self.deformer = EyeDeformer(
            texture_name=profile.name,
            pupil_warp_strength=profile.pupil_warp_strength,
        )
        self.deformer.cache.warm_up_cache(kind="spherical", verbose=True)
        self.deformer.cache.warm_up_cache(kind="pupil", verbose=True)
        self.image = profile.image
        self.width = self.height = 160
        self.gaze_cache = {}
        self.lid_control = EyelidController()

    def render_gaze_frame(self, x_off, y_off, pupil_size=1.0):
        key = self._cache_key(x_off, y_off, pupil_size)
        if key not in self.gaze_cache:
            warped = self.deformer.generate_eye_frame(
                self.image,
                pupil_size=pupil_size,
                x_off=x_off,
                y_off=y_off,
                iris_radius=self.profile.iris_radius,
                perspective_shift=self.profile.perspective_shift
            )
            cfg = self.lid_control.get_mask_config()
            left_img, right_img = apply_eyelids((warped, warped.copy()), cfg)

            left_buf  = self._get_buffer(left_img)
            right_buf = self._get_buffer(right_img)

            # Cache a pair of buffers
            self.gaze_cache[key] = (left_buf, right_buf)

        print(f"[DrawEngine] Returning gaze frame: x={x_off} y={y_off} pupil={pupil_size} key={key}")
        return self.gaze_cache[key]

    def _get_buffer(self, img):
        buf = bytearray()
        for y in range(self.height):
            for x in range(self.width):
                r, g, b = img.getpixel((x, y))
                rgb = ((r & 0xF8) << 8) | ((g & 0xFC) << 3) | (b >> 3)
                buf.append((rgb >> 8) & 0xFF)
                buf.append(rgb & 0xFF)
        return buf

    def display(self, bufs):
        # --- DIAGNOSTIC START ---
        def is_all_black(buf):
            return all(b == 0x00 for b in buf)

        if is_all_black(left_buf):
            print("[Display] Warning: LEFT buffer is fully black.")
        if is_all_black(right_buf):
            print("[Display] Warning: RIGHT buffer is fully black.")
        # --- DIAGNOSTIC END ---
        left_buf, right_buf = bufs
        # write left eye
        eye_left .set_window(0, 0, self.width - 1, self.height - 1)
        for i in range(0, len(left_buf), 1024):
            eye_left.write_data(left_buf[i:i+1024])
        # write right eye
        eye_right.set_window(0, 0, self.width - 1, self.height - 1)
        for i in range(0, len(right_buf), 1024):
            eye_right.write_data(right_buf[i:i+1024])

    def _cache_key(self, x, y, pupil):
        return (x, y, pupil)

    def apply_lids(self, bufs: tuple[bytearray, bytearray], lid_cfg: dict) -> tuple[bytearray, bytearray]:
 
        left_raw, right_raw = bufs

        def buf_to_img(buf):
            arr = np.frombuffer(buf, dtype=np.uint8).reshape((160, 160, 2))
            rgb565 = (arr[:, :, 0].astype(np.uint16) << 8) | arr[:, :, 1].astype(np.uint16)
            r = ((rgb565 >> 11) & 0x1F) << 3
            g = ((rgb565 >> 5) & 0x3F) << 2
            b = (rgb565 & 0x1F) << 3
            img = np.stack([r, g, b], axis=-1).astype(np.uint8)
            return Image.fromarray(img)

        img1 = buf_to_img(left_raw)
        img2 = buf_to_img(right_raw)
        masked_imgs = apply_eyelids((img1, img2), lid_cfg)
        print("[Lids] Applying eyelid mask to frames...")

        return tuple(self._get_buffer(img) for img in masked_imgs)
