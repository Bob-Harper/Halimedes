import asyncio
import random
from dataclasses import dataclass
from typing import Optional
import time
import os
import json
import cv2
from PIL import Image, ImageDraw
# from eyes.core.eyelid_controller import expression_map
from eyes.tools.eye_maths import quantize_pupil
from eyes.dualeye_driver import eye_left, eye_right
from helpers.global_config import EYE_ASSETS_PATH, EYE_CACHE_PATH, EYE_EXPRESSIONS_PATH, EYE_EXPRESSIONS_FILE
import numpy as np
import hashlib

expressionconfig_path = EYE_EXPRESSIONS_PATH / EYE_EXPRESSIONS_FILE
if not expressionconfig_path.exists():
    raise FileNotFoundError(f"[EyeLoader] No profile named '{EYE_EXPRESSIONS_FILE}' in {EYE_EXPRESSIONS_PATH}/")
with open(expressionconfig_path, "r") as f:
    expression_map = json.load(f)
FRAME_RATE = 60
FRAME_DURATION = 1.0 / FRAME_RATE


@dataclass
class EyeState:
    x: int = 10
    y: int = 10
    pupil: float = 1.0
    expression: str = "neutral"
    blink: float = 0.0
    eyelid_cfg: dict | None = None  # overrides from interpolated expression/blink


class EyeFrameComposer:
    def __init__(self, animator, expression_manager: Optional['EyeExpressionManager'] = None):
        self.expression_manager = expression_manager
        self.animator = animator
        self.state = EyeState()
        self._previous = EyeState()
        self.running = False
        self._dirty = True
        self._frame_drawn_event = asyncio.Event()
        
    def set_gaze(self, x: int, y: int, pupil: float):
        self.state.x = int(x)
        self.state.y = int(y)
        self.state.pupil = quantize_pupil(pupil)
        self._dirty = True

    def set_expression(self, mood: str):
        # print("EyeFrameComposer class:  async def set_expression(self, mood: str):")
        self.state.expression = mood
        self._dirty = True

    async def wait_for_frame(self):
        try:
            await asyncio.wait_for(self._frame_drawn_event.wait(), timeout=1)
        except asyncio.TimeoutError:
            print("[FrameComposer] Warning: frame draw timed out.")

    async def interpolate_gaze(self, to_x, to_y, to_pupil=1.0, steps=20, delay=0.01):
        from_x, from_y, from_pupil = self.state.x, self.state.y, self.state.pupil

        for i in range(1, steps + 1):
            frac = i / steps
            interp_x = int(from_x + (to_x - from_x) * frac)
            interp_y = int(from_y + (to_y - from_y) * frac)
            interp_pupil = quantize_pupil(from_pupil + (to_pupil - from_pupil) * frac)

            self.set_gaze(interp_x, interp_y, interp_pupil)
            self._dirty = True
            await self.wait_for_frame()
            await asyncio.sleep(delay)

    def set_eyelids(self, lid_cfg: dict | None):
        self.state.eyelid_cfg = lid_cfg
        self._dirty = True

    async def start_loop(self):
        self.running = True
        while self.running:
            if self._dirty or self.state != self._previous:
                
                if random.random() < 0.01:  # ~1% chance per frame
                    if not self.animator.blinker.is_blinking():
                        print("[Blink] Triggered")
                        self.animator.blinker.trigger()

                # Clear the event before starting a new frame render
                self._frame_drawn_event.clear()

                # Gaze update
                await asyncio.to_thread(
                    self.animator.smooth_gaze,
                    x=self.state.x, y=self.state.y, pupil=self.state.pupil
                )

                # Get lid config (either override or from expression)
                # Handle blink override if active
                dt = FRAME_DURATION  # ~0.016s at 60fps
                if self.animator.blinker and self.animator.blinker.is_blinking():
                    blink_lids = self.animator.blinker.update(dt)
                    if blink_lids:
                        lid_cfg = blink_lids
                    else:
                        lid_cfg = self.state.eyelid_cfg or self.animator.drawer.lid_control.get_mask_config()
                else:
                    lid_cfg = self.state.eyelid_cfg or self.animator.drawer.lid_control.get_mask_config()

                # Render the gaze frame
                left_buf, right_buf = await asyncio.to_thread(
                    self.animator.drawer.render_gaze_frame,
                    self.state.x, self.state.y, self.state.pupil
                )
                # assert self.expression_manager is not None
                # self.expression_manager.update()
                # expr_cfg = self.expression_manager.get_current_mask()
                # lid_cfg = expr_cfg

                # Apply lids (expression masks)
                try:
                    masked = await asyncio.to_thread(
                        self.animator.drawer.apply_lids,
                        (left_buf, right_buf), lid_cfg
                    )
                except Exception:
                    masked = (left_buf, right_buf)
            
                # Display the final frame
                await asyncio.to_thread(
                    self.animator.drawer.display,
                    masked
                )
                # Signal that the frame has been drawn
                self._frame_drawn_event.set()

                # Save the current state
                self._previous = EyeState(
                    x=self.state.x, y=self.state.y,
                    pupil=self.state.pupil,
                    expression=self.state.expression,
                    blink=self.state.blink
                )
                self._dirty = False

            await asyncio.sleep(FRAME_DURATION)


class GazeInterpolator:
    def __init__(self, animator):
        self.animator = animator  # this is EyeAnimator, to call draw_gaze()

    def interp_pupil_transition(self, from_x, from_y, to_x, to_y, from_pupil, to_pupil, steps=8, delay=0.01):
        for i in range(1, steps + 1):
            interp_x = int(from_x + (to_x - from_x) * (i / steps))
            interp_y = int(from_y + (to_y - from_y) * (i / steps))
            interp_pupil = self.animator.composer.quantize_pupil(
                from_pupil + (to_pupil - from_pupil) * (i / steps))
            self.animator.composer.set_gaze(interp_x, interp_y, pupil=interp_pupil)
            time.sleep(delay)

    async def interp_gaze_movement(self, to_x, to_y, to_pupil=1.0, steps=8, delay=0.01):
        await self.animator.composer.interpolate_gaze(to_x, to_y, to_pupil, steps, delay)

    async def translate_gaze_mode(self, mode):
        modes = {
            "left": (10, 20),
            "right": (10, 0),
            "up": (20, 10),
            "down": (0, 10),
            "center": (10, 10),
            "wander": (
                random.randint(0, 20),
                random.randint(0, 20)
            )
        }
        if mode not in modes:
            print(f"[GazeInterpolator] Unknown mode: {mode}")
            return

        to_x, to_y = modes[mode]
        # to_pupil = random.uniform(0.85, 1.2) if mode == "wander" else 1.0
        to_pupil = 1.0
        await self.interp_gaze_movement(to_x, to_y, to_pupil)


class EyeAnimator:
    def __init__(self, profile):
        self.profile = profile
        self.state = {
            "x": 10,
            "y": 10,
            "pupil": 1.0
        }
        self.composer = EyeFrameComposer(self, None)
        self.drawer = DrawEngine(profile)
        self.blinker = BlinkAnimator(
            expression_getter=self.drawer.lid_control.get_mask_config,
            duration=profile.close_speed,
            hold=profile.hold
        )
        self.interpolator = GazeInterpolator(self)
        self.drawer.gaze_cache.clear()  # clear the gaze cache
        self.last_buf = None  # clear the last buffer for blinking
        self.current_expression = None  # track what’s live now
        # create a blank gaze buffer to seed last_buf
        left, right = self.drawer.render_gaze_frame(10, 10, 1.0)
        self.last_buf = (left, right)
        from eyes.dualeye_driver import eye_left, eye_right
        for eye in (eye_left, eye_right):
            eye.fill_screen(0x0000)  # clear both displays black
        time.sleep(0.1)  # short SPI bus stabilization

    async def smooth_gaze(self, x, y, pupil=1.0):
        await self.interpolator.interp_gaze_movement(x, y, pupil)

    async def animate_expression(self, mood: str, steps=16, delay=0.01):
        # print(f"[Animator] Tweening to expression '{mood}'")

        target = self.drawer.lid_control.expression_map.get(mood)
        if not target:
            print(f"[EyeAnimator] Unknown expression: {mood}")
            return

        start_cfg = self.drawer.lid_control.lids.copy()
        for step in range(1, steps + 1):
            frac = step / steps
            interp_cfg = {
                k: int(start_cfg.get(k, 0) + (target.get(k, 0) - start_cfg.get(k, 0)) * frac)
                for k in target
            }
            self.drawer.lid_control.lids.update(interp_cfg)
            self.current_expression = mood

            # Hand off the current state to Composer
            self.composer.set_eyelids(interp_cfg)
            await asyncio.sleep(delay)

        self.composer.set_eyelids(None)  # release override once tween done

class DrawEngine:
    def __init__(self, profile):
        self.profile = profile
        self.deformer = EyeDeformer(
            texture_name=profile.name,
            pupil_warp_strength=profile.pupil_warp_strength,
        )
        # self.deformer.cache.warm_up_cache(kind="spherical", verbose=False)
        # self.deformer.cache.warm_up_cache(kind="pupil", verbose=False)
        # 10,000 plus cache files, crash pi, bad news, remove until/if we add alternate
        # cache warmup.  will be testing eventually with things like maxfiles
        self.animation_style = profile.animation_style
        # Convert PIL image to NumPy array once here
        if isinstance(profile.image, Image.Image):
            self.image = np.array(profile.image)
        else:
            self.image = profile.image
        self.width = self.height = 160
        self.gaze_cache = {}
        self.lid_control = EyelidController()
        self._lid_mask_cache = {}

    def _mask_key(self, cfg):
        return tuple(cfg.values())

    def _get_lid_mask(self, lid_cfg):
        key = self._mask_key(lid_cfg)
        if key not in self._lid_mask_cache:
            self._lid_mask_cache[key] = self._make_mask_images(lid_cfg)
        return self._lid_mask_cache[key]
    
    def _make_mask_images(self, cfg: dict) -> tuple[Image.Image, Image.Image]:
        w, h = self.width, self.height

        def make_mask(tl, tr, bl, br):
            m = Image.new("L", (w, h), 255)
            d = ImageDraw.Draw(m)
            d.polygon([(0,0),(w,0),(w, tr),(0, tl)], fill=0)
            d.polygon([(0,h),(w,h),(w, h - br),(0, h - bl)], fill=0)
            return m

        m1 = make_mask(cfg["eye1_top_left"], cfg["eye1_top_right"],
                    cfg["eye1_bottom_left"], cfg["eye1_bottom_right"])
        m2 = make_mask(cfg["eye2_top_left"], cfg["eye2_top_right"],
                    cfg["eye2_bottom_left"], cfg["eye2_bottom_right"])
        return m1, m2


    def _apply_mask_np(self, img: Image.Image, mask: Image.Image) -> Image.Image:
        arr = np.asarray(img)
        mask_arr = np.asarray(mask, dtype=bool)

        if arr.ndim == 3 and arr.shape[2] == 3:
            arr[~mask_arr] = [0, 0, 0]
        else:
            arr[~mask_arr] = 0

        return Image.fromarray(arr)
    
    def render_gaze_frame(self, x_off, y_off, pupil_size=1.0):
        key = self._cache_key(x_off, y_off, pupil_size)
        if key not in self.gaze_cache:
            warped = self.deformer.generate_eye_frame(
                self.image,
                pupil_size=pupil_size,
                x_off=x_off,
                y_off=y_off,
                iris_radius=self.profile.iris_radius,
                perspective_shift=self.profile.perspective_shift,
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
            print("[DrawEngine] Invalid buffer passed to display. Skipping.")
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

        m1, m2 = self._get_lid_mask(lid_cfg)
        masked_left_img  = self._apply_mask_np(img1, m1)
        masked_right_img = self._apply_mask_np(img2, m2)

        left_buf  = self._get_buffer(masked_left_img)
        right_buf = self._get_buffer(masked_right_img)
        return left_buf, right_buf

class BlinkAnimator:
    def __init__(self, expression_getter, duration=0.15, hold=0.08):
        self.expression_getter = expression_getter  # callback to query expression config
        self.duration = duration
        self.hold = hold
        self.timer = 0.0
        self.active = False
        self.phase = None  # 'closing', 'holding', 'opening'

        self.closed_cfg = {
            "eye1_top_left": 0, "eye1_top_right": 0,
            "eye1_bottom_left": 0, "eye1_bottom_right": 0,
            "eye2_top_left": 0, "eye2_top_right": 0,
            "eye2_bottom_left": 0, "eye2_bottom_right": 0,
        }

    def trigger(self):
        self.timer = 0.0
        self.active = True
        self.phase = 'closing'

    def is_blinking(self):
        return self.active

    def update(self, dt):
        if not self.active:
            return None

        self.timer += dt

        if self.phase == 'closing':
            if self.timer >= self.duration:
                self.phase = 'holding'
                self.timer = 0.0
            t = self.timer / self.duration
            return self._interpolate(self.expression_getter(), self.closed_cfg, t)

        elif self.phase == 'holding':
            if self.timer >= self.hold:
                self.phase = 'opening'
                self.timer = 0.0
            return self.closed_cfg

        elif self.phase == 'opening':
            if self.timer >= self.duration:
                self.active = False
                self.phase = None
                return None
            t = self.timer / self.duration
            return self._interpolate(self.closed_cfg, self.expression_getter(), t)

    def _interpolate(self, from_cfg, to_cfg, t):
        return {
            k: int(round((1 - t) * from_cfg[k] + t * to_cfg[k]))
            for k in from_cfg
        }


class EyelidController:
    def __init__(self):
        neutral = expression_map.get("neutral", {})
        # ensure all four corners exist
        self.lids = {
            "eye1_top_left":        neutral.get("eye1_top_left",    36),
            "eye1_top_right":       neutral.get("eye1_top_right",   40),
            "eye1_bottom_left":     neutral.get("eye1_bottom_left",  0),
            "eye1_bottom_right":    neutral.get("eye1_bottom_right", 0),
            "eye2_top_left":        neutral.get("eye2_top_left",    36),
            "eye2_top_right":       neutral.get("eye2_top_right",   36),
            "eye2_bottom_left":     neutral.get("eye2_bottom_left",  40),
            "eye2_bottom_right":    neutral.get("eye2_bottom_right", 40),
        }
        self.expression_map = expression_map

    def set_eyelid_expression(self, name: str):
        print(f"[LidController] Switching to expression: {name}")
        exp = self.expression_map.get(name)
        if not exp:
            print(f"[EyelidController] Unknown expression: {name}")
            return
        # copy over only the keys we care about
        for corner in (
            "eye1_top_left","eye1_top_right",
            "eye1_bottom_left","eye1_bottom_right",
            "eye2_top_left","eye2_top_right",
            "eye2_bottom_left","eye2_bottom_right"
        ):
            if corner in exp:
                self.lids[corner] = exp[corner]

    def get_mask_config(self) -> dict:
        lids = self.lids
        print(f"[get_current_mask] Current mask: {lids}")
        return lids


class EyeExpressionManager:
    def __init__(self, animator, composer, multi_file=False):
        self.animator = animator
        self.composer = composer
        self.multi_file = multi_file
        self.lid_control = EyelidController()
        self.expressions = self._load_expressions()
        self.state = EyeState()

    async def set_expression(self, mood: str):
        print(f"[ExpressionManager] Animate expression: {mood}")
        await self.animator.animate_expression(mood)

    def _load_expressions(self):
        expressions = {}
        base_dir = os.path.dirname(__file__)
        expr_path = os.path.join(base_dir, "expressions/eye_expressions.json")

        if self.multi_file:
            for file in os.listdir(base_dir):
                if file.endswith(".json") and file != "expressions/eye_expressions.json":
                    path = os.path.join(base_dir, file)
                    try:
                        with open(path, "r") as f:
                            name = os.path.splitext(file)[0]
                            expressions[name] = json.load(f)
                    except Exception as e:
                        print(f"[ExpressionManager] Failed to load {file}: {e}")
        else:
            try:
                with open(expr_path, "r") as f:
                    expressions = json.load(f)
            except Exception as e:
                print(f"[ExpressionManager] Failed to load expressions: {e}")
        return expressions

    def update(self):
        if self.composer.state.expression:
            self.lid_control.set_eyelid_expression(self.composer.state.expression)
            self.composer.set_eyelids(self.lid_control.get_mask_config())
        else:
            self.composer.set_eyelids(None)

    def get_current_mask(self):
        # Return the current eyelid mask configuration
        return self.lid_control.get_mask_config()


class EyeCacheManager:
    def __init__(self, texture_name="default"):
        self.base_dir = EYE_CACHE_PATH
        self.texture_name = texture_name

        self.pupil_dir = self.base_dir / texture_name / "pupil"
        self.spherical_dir = self.base_dir / texture_name / "spherical"
        self.gaze_dir = self.base_dir / texture_name / "gaze"
        self.lid_mask_dir = self.base_dir / texture_name / "lids"

        self.pupil_dir.mkdir(parents=True, exist_ok=True)
        self.spherical_dir.mkdir(parents=True, exist_ok=True)
        self.gaze_dir.mkdir(parents=True, exist_ok=True)
        self.lid_mask_dir.mkdir(parents=True, exist_ok=True)

        self.pupil_maps = {}
        self.spherical_maps = {}
        self.gaze_cache = {}
        self.lid_mask_cache = {}

    def _generate_key(self, **kwargs):
        key_string = "_".join(f"{k}:{v}" for k, v in sorted(kwargs.items()))
        return hashlib.md5(key_string.encode()).hexdigest()

    def _get_path(self, key_dict, kind="pupil"):
        filename = self._generate_key(**key_dict)
        ext = ".npz" if kind == "spherical" else ".npy"
        target_dir = self.spherical_dir if kind == "spherical" else self.pupil_dir
        return target_dir / f"{filename}{ext}"

    def save_map(self, key_dict, data, kind="pupil"):
        path = self._get_path(key_dict, kind)
        if kind == "spherical":
            np.savez_compressed(path, map_x=data[0], map_y=data[1])
        else:
            np.save(path, data)

    def load_map(self, key_dict, kind="pupil"):
        key = self._generate_key(**key_dict)

        if kind == "pupil" and key in self.pupil_maps:
            return self.pupil_maps[key]

        if kind == "spherical" and key in self.spherical_maps:
            return self.spherical_maps[key]

        # Not in memory, attempt to load from disk
        file_path = self._get_path(key_dict, kind)
        if not file_path.exists():
            return None  # If no existing cache, get_or_generate will create a new one

        try:
            if kind == "spherical":
                with np.load(file_path, allow_pickle=True) as data:
                    result = (data["map_x"], data["map_y"])
                    self.spherical_maps[key] = result
                    return result
            else:
                data = np.load(file_path, allow_pickle=True)
                self.pupil_maps[key] = data
                return data
        except Exception:
            try:
                file_path.unlink()
            except:
                pass
            return None

    def exists(self, key_dict, kind="pupil"):
        return self._get_path(key_dict, kind).exists()

    def warm_up_cache(self, kind="pupil", verbose=False, max_files=None):
        ext = ".npz" if kind == "spherical" else ".npy"
        cache_dir = self.pupil_dir if kind == "pupil" else self.spherical_dir
        log_file = self.base_dir / f"bad_cache_{kind}.log"

        map_dict = self.pupil_maps if kind == "pupil" else self.spherical_maps
        map_dict.clear()

        loaded = 0
        skipped = 0
        deleted = 0
        errors = []

        files = list(cache_dir.glob(f"*{ext}"))
        total_files = len(files)

        if max_files is not None:
            files = files[:max_files]

        if verbose:
            print(f"[Cache Warm-Up] Loading {len(files)} {kind} files into memory (of {total_files} total)...")

        for file in files:
            try:
                key = file.stem

                if ext == ".npy":
                    data = np.load(file)
                    if data is None or not hasattr(data, 'shape'):
                        raise ValueError("Empty or malformed .npy")
                    map_dict[key] = data

                else:
                    with np.load(file) as data:
                        if "map_x" not in data or "map_y" not in data:
                            raise ValueError("Missing keys in .npz")
                        map_dict[key] = (data["map_x"], data["map_y"])

                loaded += 1

            except Exception as e:
                error_msg = f"{file.name} - {e}"
                errors.append(error_msg)
                if verbose:
                    print(f"[Cache Warm-Up] Corrupt: {error_msg}")
                try:
                    file.unlink()
                    deleted += 1
                except Exception as del_err:
                    err_msg = f"Failed to delete {file.name} - {del_err}"
                    errors.append(err_msg)
                    if verbose:
                        print(f"[Cache Warm-Up] {err_msg}")
                skipped += 1

        if errors:
            with open(log_file, "a") as log:
                log.write(f"\n[Run at {time.ctime()}] Errors in {kind} cache:\n")
                for e in errors:
                    log.write(f"- {e}\n")

        if verbose:
            print(f"[Cache Warm-Up] Done. Loaded: {loaded}, Deleted: {deleted}, Errors: {len(errors)}")

        return loaded


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


class EyeConfig:
    def __init__(self, name, config_path, config, image):
        self.name = name
        self.image = image
        self.config_path = config_path
        self.texture_path = config["image_path"]
        self.directional = config.get("directional", False)
        self.iris_radius = config.get("iris_radius", 42)
        self.pupil_min = config.get("pupil_min", 0.5)
        self.pupil_max = config.get("pupil_max", 1.5)
        self.pupil_warp_strength = config.get("pupil_warp_strength", 1.0)
        self.perspective_shift = config.get("perspective_shift", 0.02)
        self.x_off = config.get("x_off", 10)
        self.y_off = config.get("y_off", 10)
        self.close_speed = config.get("close_speed", 0.01)
        self.open_speed = config.get("open_speed", 0.03)
        self.hold = config.get("hold", 0.08)
        self.animation_style = config.get("animation_style", "default")
        self.expression_profile = config.get("expression_profile", "default")
        self.use_case = config.get("use_case", "default")


# End of Classes

def load_eye_profile(profile_name):
    config_path = EYE_ASSETS_PATH / f"{profile_name}.json"

    if not config_path.exists():
        raise FileNotFoundError(f"[EyeLoader] No profile named '{profile_name}' in {config_path}/")

    with open(config_path, "r") as f:
        config = json.load(f)

    # Resolve texture path relative to the config file
    texture_path = (config_path.parent / config["image_path"]).resolve()
    if not texture_path.exists():
        raise FileNotFoundError(f"[EyeLoader] Texture file '{texture_path}' not found.")

    img = Image.open(texture_path).convert("RGB")

    if img.width != img.height:
        print(f"[WARNING] Eye texture is not square ({img.width}x{img.height})")
    if img.width != 180:
        img = img.resize((180, 180), resample=Image.Resampling.LANCZOS)
    if config.get("directional", False):
        img = img.rotate(90, expand=True)

    return EyeConfig(profile_name, config_path, config, img)
