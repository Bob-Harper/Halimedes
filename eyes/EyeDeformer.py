import numpy as np
from eyes.EyeCacheManager import EyeCacheManager
from eyes.tools.eye_maths import quantize_pupil
import cv2
from PIL import Image


class EyeDeformer:
    def __init__(
            self,
            pupil_warp_strength=1.0,
            texture_name="default",
            animation_style="default",
            verbose=False
            ):
        self.cache = EyeCacheManager(texture_name=texture_name)
        self.warp_strength = pupil_warp_strength
        self.animation_style="default"
        self.verbose = verbose

    def generate_eye_frame(
        self,
        source_img,
        pupil_size=1.0,
        x_off=10,
        y_off=10,
        iris_radius=42,
        perspective_shift=0.02,
        animation_style=None
    ):
        style = animation_style or self.animation_style

        if style == "vector":
            warped_pupil = np.array(source_img)
        else:
            pupil_maps = self.get_or_generate_pupil_warp_map(
                pupil_size=pupil_size,
                iris_radius=iris_radius,
            )
            warped_pupil = self.apply_pupil_warp(source_img, *pupil_maps)

        final_img = self.apply_spherical_warp(
            warped_pupil,
            x_off=x_off,
            y_off=y_off,
            strength=perspective_shift
        )
        return_image = Image.fromarray(final_img, mode='RGB')
        return return_image

    def get_or_generate_spherical_map(self, x_off=10, y_off=10, strength=0.03):
        key_dict = {
            "x_off": x_off,
            "y_off": y_off,
            "strength": round(float(strength), 4)
        }

        cached = self.cache.load_map(key_dict, kind="spherical")
        if cached is not None:
            return cached
        h = w = 180
        center_x = w // 2
        center_y = h // 2

        norm_x = (x_off - 10) / 10.0
        norm_y = (y_off - 10) / 10.0

        yy, xx = np.meshgrid(np.arange(0, 180), np.arange(0, 180), indexing='xy')
        dx = (xx - center_x) / center_x # type: ignore
        dy = (yy - center_y) / center_y
        r = np.sqrt(dx**2 + dy**2)
        z = np.sqrt(1.0 - np.clip(r**2, 0, 1))

        shift_scale = strength / 2
        dx += norm_x * shift_scale * z
        dy += norm_y * shift_scale * z

        map_x = (dx * center_x + center_x).astype(np.float32) # type: ignore
        map_y = (dy * center_y + center_y).astype(np.float32)

        self.cache.save_map(key_dict, (map_x, map_y), kind="spherical")
        return map_x, map_y

    def apply_spherical_warp(self, image, x_off=10, y_off=10, strength=0.03):
        map_x, map_y = self.get_or_generate_spherical_map(x_off, y_off, strength)
        result = cv2.remap(image, map_x, map_y, interpolation=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
        if result.dtype != np.uint8:
            result = np.clip(result, 0, 255).astype(np.uint8)
        return result

    def get_or_generate_pupil_warp_map(self, pupil_size, iris_radius):

        pupil_size = quantize_pupil(pupil_size)  # ensures stable keys

        key_dict = {
            "pupil_size": pupil_size,
            "iris_radius": iris_radius,
            "warp_strength": self.warp_strength,
        }
        cached = self.cache.load_map(key_dict, kind="pupil")
        if cached is not None:
            return cached
        h = w = 180
        center_x = w // 2
        center_y = h // 2
        yy, xx = np.meshgrid(np.arange(h), np.arange(w), indexing='xy')
        dx = xx - center_x
        dy = yy - center_y
        radius = np.sqrt(dx**2 + dy**2)
        angle  = np.arctan2(dy, dx)

        delta = pupil_size - 1.0
        scale = 1.0 - delta * self.warp_strength

        norm = np.clip(radius / iris_radius, 0.0, 1.0)
        warp_factor = 1 + (scale - 1) * (1 - norm)**2

        warped_radius = radius * warp_factor
        warped_radius[radius > iris_radius] = radius[radius > iris_radius]

        sample_x = warped_radius * np.cos(angle) + center_x
        sample_y = warped_radius * np.sin(angle) + center_y

        self.cache.save_map(key_dict, (sample_x, sample_y), kind="pupil")
        return sample_x, sample_y

    def apply_pupil_warp(self, source_img, sample_x, sample_y):
        src_np = np.array(source_img)
        h, w = src_np.shape[:2]

        x0 = np.floor(sample_x).astype(np.int32)
        y0 = np.floor(sample_y).astype(np.int32)
        x1 = np.clip(x0 + 1, 0, w - 1)
        y1 = np.clip(y0 + 1, 0, h - 1)
        x0 = np.clip(x0, 0, w - 1)
        y0 = np.clip(y0, 0, h - 1)

        wx = sample_x - x0
        wy = sample_y - y0

        wa = (1 - wx) * (1 - wy)
        wb = wx * (1 - wy)
        wc = (1 - wx) * wy
        wd = wx * wy

        warped = np.zeros_like(src_np)
        for c in range(3):
            a = src_np[y0, x0, c]
            b = src_np[y0, x1, c]
            c_ = src_np[y1, x0, c]
            d = src_np[y1, x1, c]
            warped[..., c] = (
                wa * a + wb * b + wc * c_ + wd * d
            ).astype(np.uint8)

        return warped
    