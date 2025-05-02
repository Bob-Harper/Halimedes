from PIL import Image
import numpy as np
import cv2
from eyes.eye_cache_manager import EyeCacheManager


class EyeDeformer:
    def __init__(
            self, 
            sclera_size=85, 
            output_size=160, 
            texture_name="default", 
            pupil_warp_strength=1.0
            ):
        self.sclera_size = sclera_size
        self.output_size = output_size
        self.cache = EyeCacheManager(texture_name=texture_name)
        self.cache.warm_up_cache("pupil")
        self.warp_strength = pupil_warp_strength
        print(f"[Deformer INIT] warp_strength = {self.warp_strength}")

    
    def generate_eye_frame(
        self,
        source_img,
        pupil_size=1.0,
        x_off=10,
        y_off=10,
        iris_radius=42,
        feather_width=8,
        perspective_shift=0.02,
        output_size=160
    ):
        """
        1) Pupil warp → cache keyed on pupil_size, iris_radius, feather_width
        2) Gaze‐aligned crop
        3) Spherical warp → cache keyed on x_off, y_off, strength
        """

        # --- 1) Pupil layer ---
        pupil_maps = self.get_or_generate_pupil_warp_map(
            pupil_size=pupil_size,
            iris_radius=iris_radius,
            feather_width=feather_width
        )
        warped_pupil = self.apply_pupil_warp(source_img, *pupil_maps)

        # --- 2) Gaze align ---
        gaze_aligned = self.crop_to_display(warped_pupil, x_off, y_off, output_size)

        # --- 3) Spherical layer ---
        final_img = self.apply_spherical_warp(
            gaze_aligned,
            x_off=x_off,
            y_off=y_off,
            strength=perspective_shift
        )

        # No eyelid masking here—draw_engine will apply that as a separate layer
        return Image.fromarray(final_img.astype(np.uint8), mode='RGB')



    def get_or_generate_spherical_map(self, x_off=10, y_off=10, strength=0.03):
        key_dict = {
            "x_off": x_off,
            "y_off": y_off,
            "strength": round(float(strength), 4)
        }

        cached = self.cache.load_map(key_dict, kind="spherical")
        if cached is not None:
            # print(f"[get_or_generate_spherical_map] Using preloaded spherical map for key {key_dict}")
            return cached
        # print("[get_or_generate_spherical_map] calculating realtime spherical map, no key_dict found")

        # Generate map
        h = w = 180
        center_x = w // 2
        center_y = h // 2

        norm_x = (x_off - 10) / 10.0
        norm_y = (y_off - 10) / 10.0

        yy, xx = np.meshgrid(np.arange(h), np.arange(w), indexing='xy')
        dx = (xx - center_x) / center_x
        dy = (yy - center_y) / center_y
        r = np.sqrt(dx**2 + dy**2)
        z = np.sqrt(1.0 - np.clip(r**2, 0, 1))

        shift_scale = strength / 2  # or even 0.75 depending on lens type
        dx += norm_x * shift_scale * z
        dy += norm_y * shift_scale * z

        map_x = (dx * center_x + center_x).astype(np.float32)
        map_y = (dy * center_y + center_y).astype(np.float32)

        self.cache.save_map(key_dict, (map_x, map_y), kind="spherical")
        return map_x, map_y

    def apply_spherical_warp(self, image, x_off=10, y_off=10, strength=0.03):
        map_x, map_y = self.get_or_generate_spherical_map(x_off, y_off, strength)
        return cv2.remap(image, map_x, map_y, interpolation=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)

    def get_or_generate_pupil_warp_map(self, pupil_size, iris_radius, feather_width):
        # 1) Build the cache key and try loading (you can leave this or comment it out while debugging)
        key_dict = {
            "pupil_size":    round(float(pupil_size), 3),
            "iris_radius":   iris_radius,
            "feather_width": feather_width,
            "warp_strength": self.warp_strength,
        }
        cached = self.cache.load_map(key_dict, kind="pupil")
        if cached is not None:
            return cached

        # 2) Regenerate the map from scratch
        h = w = 180
        center_x = w // 2
        center_y = h // 2
        yy, xx = np.meshgrid(np.arange(h), np.arange(w), indexing='xy')
        dx = xx - center_x
        dy = yy - center_y
        radius = np.sqrt(dx**2 + dy**2)
        angle  = np.arctan2(dy, dx)

        # 3) Compute scale factor
        delta = pupil_size - 1.0
        scale = 1.0 - delta * self.warp_strength

        # 4) Compute warp
        norm = np.clip(radius / iris_radius, 0.0, 1.0)
        
        # warp_factor = 1 + (scale - 1) * (1 - norm)  # Linear warp gentle taper
        warp_factor = 1 + (scale - 1) * (1 - norm)**2  # Quadratic warp normal taper
        # warp_factor = 1 + (scale - 1) * (1 - norm**2)  # Quadratic warp stronger taper
        # warp_factor = 1 + (scale - 1) * (1 - norm)**3  # Cubic warp stupidly strong taper

        # 5) Apply it
        warped_radius = radius * warp_factor

        # 6) Leave all outside the iris untouched
        warped_radius[radius > iris_radius] = radius[radius > iris_radius]

        # 8) Convert radii back to x/y sampling coords
        sample_x = warped_radius * np.cos(angle) + center_x
        sample_y = warped_radius * np.sin(angle) + center_y

        # 9) Cache & return
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

    def crop_to_display(self, image, x_off, y_off, output_size=160):
        h, w = image.shape[:2]
        center_x = w // 2
        center_y = h // 2
        crop_x = center_x - output_size // 2 + (x_off - 10)
        crop_y = center_y - output_size // 2 + (y_off - 10)
        crop_x = np.clip(crop_x, 0, w - output_size)
        crop_y = np.clip(crop_y, 0, h - output_size)
        return image[crop_y:crop_y + output_size, crop_x:crop_x + output_size]
    
"""             
    def get_or_generate_pupil_warp_map(self, pupil_size, iris_radius, feather_width):
        # Build the cache key
        key_dict = {
            "pupil_size": round(float(pupil_size), 3),
            "iris_radius": iris_radius,
            "feather_width": feather_width,
        }

        # Try loading from cache
        cached = self.cache.load_map(key_dict, kind="pupil")
        if cached is not None:
            # The cache should store a tuple (sample_x, sample_y)
            try:
                sample_x, sample_y = cached
                return sample_x, sample_y
            except Exception as e:
                print(f"[PupilWarp] ERROR unpacking cached data for {key_dict}: {e!r}")

        # Cache miss or unpack failure → regenerate the maps
        print(f"[PupilWarp] Generating new map for key {key_dict}")

        # Prepare coordinate grid
        h = w = 180
        center_x = w // 2
        center_y = h // 2
        yy, xx = np.meshgrid(np.arange(h), np.arange(w), indexing='xy')
        dx = xx - center_x
        dy = yy - center_y
        radius = np.sqrt(dx**2 + dy**2)
        angle = np.arctan2(dy, dx)

        # Apply scale inside the iris
        # scale = float(pupil_size)

        # Use the configured warp_strength
        delta = pupil_size - 1.0
        scale = 1.0 - delta * self.warp_strength

        # prepare warped_radius defaulting to identity everywhere
        warped_radius = radius.copy()

        # 1) Inner iris: warp by scale
        inner = radius <= iris_radius
        warped_radius[inner] = radius[inner] * scale

        # 2) Feather zone: blend back to identity
        if feather_width > 0:
            feather = (radius > iris_radius) & (radius <= iris_radius + feather_width)
            t = (radius[feather] - iris_radius) / feather_width
            warped_radius[feather] = (
                warped_radius[feather] * (1 - t) +
                radius[feather]        * t
            )

        # 3) Outer zone: do nothing – warped_radius already == radius

        # NO global clipping here!
        # warped_radius stays > iris_radius for outer pixels, sampling identity.

        # finally compute sample coords
        sample_x = warped_radius * np.cos(angle) + center_x
        sample_y = warped_radius * np.sin(angle) + center_y
        # Save to cache for next time
        self.cache.save_map(key_dict, (sample_x, sample_y), kind="pupil")

        return sample_x, sample_y
 """