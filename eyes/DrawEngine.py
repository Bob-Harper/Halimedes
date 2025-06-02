import numpy as np
from eyes.EyeDeformer import EyeDeformer
from eyes.dualeye_driver import eye_left, eye_right
from PIL import Image, ImageDraw


class DrawEngine:
    def __init__(self, eye_profile):
        self.profile = eye_profile
        self.deformer = EyeDeformer(
            texture_name=eye_profile.name,
            pupil_warp_strength=eye_profile.pupil_warp_strength,
        )
        self.animation_style = eye_profile.animation_style
        # Convert PIL image to NumPy array once here
        if isinstance(eye_profile.image, Image.Image):
            eye_img = eye_profile.image.resize((180, 180))  # ← if needed, do it here
            self.image = np.array(eye_img)
        else:
            self.image = eye_profile.image
        self.width = self.height = 160
        self.gaze_cache = {}
        self._lid_mask_cache = {}

    def _mask_key(self, cfg):
        # print("[DrawEngine] qaz Generating mask key with cfg:", cfg)
        return tuple(cfg.values())

    def _get_lid_mask(self, lid_cfg):
        key = self._mask_key(lid_cfg)
        if key not in self._lid_mask_cache:
            self._lid_mask_cache[key] = self._make_mask_images(lid_cfg)
        # print("[DrawEngine] wsx Generating mask with cfg:", lid_cfg)
    
        return self._lid_mask_cache[key]

    def _make_mask_images(self, cfg: dict) -> tuple[Image.Image, Image.Image]:
        # print("[DrawEngine] edc Making mask images with cfg:", cfg)
        w, h = self.width, self.height

        def make_mask(tl, tr, bl, br):
            m = Image.new("L", (w, h), 255)
            d = ImageDraw.Draw(m)
            d.polygon([(0,0),(w,0),(w, tr),(0, tl)], fill=0)
            d.polygon([(0,h),(w,h),(w, h - br),(0, h - bl)], fill=0)
            # print("[DrawEngine] rfv Created mask with corners:", tl, tr, bl, br)
            d.polygon([(0,0),(tl,0),(tr,0),(w,0)], fill=0)
            return m

        m1 = make_mask(cfg["eye1_top_left"], cfg["eye1_top_right"],
                    cfg["eye1_bottom_left"], cfg["eye1_bottom_right"])
        m2 = make_mask(cfg["eye2_top_left"], cfg["eye2_top_right"],
                    cfg["eye2_bottom_left"], cfg["eye2_bottom_right"])
        return m1, m2

    def _apply_mask_np(self, img: Image.Image, mask: Image.Image) -> Image.Image:
        arr = np.array(img)
        mask_arr = np.array(mask)
        # print("[DrawEngine] tgb Applying mask to image with shape:", arr.shape, "and mask shape:", mask_arr.shape)
        # Ensure mask is broadcastable
        if mask_arr.ndim == 2 and arr.ndim == 3:
            mask_arr = np.expand_dims(mask_arr, axis=2)  # (H, W) → (H, W, 1)

        # Create a black image
        black = np.zeros_like(arr)
        # print("[DrawEngine] yhn Creating black image with shape:", black.shape)
        # Where mask is 0, apply black
        result = np.where(mask_arr == 0, black, arr)

        return Image.fromarray(result.astype(np.uint8))


    def render_gaze_frame(self, x, y, pupil_scale=1.0):
        key = self._cache_key(x, y, pupil_scale)
        if key not in self.gaze_cache:
            warped = self.deformer.generate_eye_frame(
                self.image,
                pupil_scale=pupil_scale,
                x=x,
                y=y,
                iris_radius=self.profile.iris_radius,
                gaze_perspective_shift=self.profile.gaze_perspective_shift,
                animation_style=self.animation_style
            )
            left_img = warped
            right_img = warped.copy()
            left_buf  = self._get_buffer(left_img)
            right_buf = self._get_buffer(right_img)
            # Cache a pair of buffers
            self.gaze_cache[key] = (left_buf, right_buf)

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

        if not bufs or not isinstance(bufs, tuple) or len(bufs) != 2:
            # print("[DrawEngine] Invalid buffer passed to display. Skipping.")
            return

        left_buf, right_buf = bufs

        # write left eye
        eye_left.set_window(0, 0, self.width - 1, self.height - 1)
        for i in range(0, len(left_buf), 1024):
            eye_left.write_data(left_buf[i:i+1024])

        # write right eye
        eye_right.set_window(0, 0, self.width - 1, self.height - 1)
        for i in range(0, len(right_buf), 1024):
            eye_right.write_data(right_buf[i:i+1024])

    def _cache_key(self, x, y, pupil):
        return (x, y, pupil)

    def apply_lids(
        self,
        bufs: tuple[bytearray, bytearray],
        lid_cfg: dict
        ) -> tuple[bytearray, bytearray]:
        left_raw, right_raw = bufs
        # print("[DrawEngine] ujm Applying lids with config:", lid_cfg)
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
        # print("[DrawEngine] iki Converted buffers to images for lid application.")
        m1, m2 = self._get_lid_mask(lid_cfg)
        masked_left_img  = self._apply_mask_np(img1, m1)
        masked_right_img = self._apply_mask_np(img2, m2)

        left_buf  = self._get_buffer(masked_left_img)
        right_buf = self._get_buffer(masked_right_img)
        # print("[DrawEngine] olo Applied masks to images and converted back to buffers.")
        return left_buf, right_buf
