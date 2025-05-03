from eyes.dualeye_driver import eye_left, eye_right
from .eyelid_masker import apply_eyelids
from .eyelid_controller import EyelidController
from .eye_deform import EyeDeformer

class DrawEngine:
    def __init__(self, profile):
        self.profile = profile
        self.deformer = EyeDeformer(
            sclera_size=profile.sclera_size,
            texture_name=profile.name,
            pupil_warp_strength=profile.pupil_warp_strength,
        )
        self.deformer.cache.warm_up_cache(kind="spherical", verbose=True)
        self.deformer.cache.warm_up_cache(kind="pupil", verbose=True)
        self.image = profile.image
        self.eyelids = {
            'top': profile.eyelid_top,
            'bottom': profile.eyelid_bottom,
            'left': profile.eyelid_left,
            'right': profile.eyelid_right,
        }
        self.width = self.height = 160
        self.gaze_cache = {}
        self.lid_control = EyelidController()

    def generate_frame(self, x_off, y_off, pupil_size=1.0):
        key = self._cache_key(x_off, y_off, pupil_size)
        if key not in self.gaze_cache:
            warped = self.deformer.generate_eye_frame(
                self.image,
                pupil_size=pupil_size,
                x_off=x_off,
                y_off=y_off,
                iris_radius=self.profile.iris_radius,
                feather_width=self.profile.feather_width,
                perspective_shift=self.profile.perspective_shift
            )
        config = self.lid_control.get_mask_config()
        masked = apply_eyelids(warped, config)
        self.gaze_cache[key] = self._get_buffer(masked)
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

    def display(self, buf):
        for eye in (eye_left, eye_right):
            eye.set_window(0, 0, self.width - 1, self.height - 1)
            for i in range(0, len(buf), 1024):
                eye.write_data(buf[i:i + 1024])

    def _cache_key(self, x, y, pupil):
        lids = self.lid_control.get_mask_config()
        return (x, y, pupil, lids["top"], lids["bottom"], lids["left"], lids["right"])
