import asyncio
import random
from dataclasses import dataclass
import time
import os
import json
import cv2
from PIL import Image, ImageDraw
# from eyes.core.eyelid_controller import expression_map
from eyes.dualeye_driver import eye_left, eye_right
from helpers.global_config import EYE_ASSETS_PATH, EYE_CACHE_PATH, EYE_EXPRESSIONS_PATH, EYE_EXPRESSIONS_FILE
import numpy as np
import hashlib

expressionconfig_path = EYE_EXPRESSIONS_PATH / EYE_EXPRESSIONS_FILE
if not expressionconfig_path.exists():
    raise FileNotFoundError(f"[EyeLoader] No profile named '{EYE_EXPRESSIONS_FILE}' in {EYE_EXPRESSIONS_PATH}/")
with open(expressionconfig_path, "r") as f:
    expression_map = json.load(f)
"""
eye_expressions.json schema:

Each expression dict may contain:
    "test": {
        "eye1_top_left": 0,     -- Left eye, top eyelid, left corner
        "eye1_top_right": 0,    -- Left eye, top eyelid, right corner
        "eye1_bottom_left": 0,  -- Left eye, bottom eyelid, left corner 
        "eye1_bottom_right": 0, -- Left eye, bottom eyelid, right corner
        "eye2_top_left": 0,     -- Right eye, top eyelid, left corner
        "eye2_top_right": 0,    -- Right eye, top eyelid, right corner
        "eye2_bottom_left": 0,  -- Right eye, bottom eyelid, left corner
        "eye2_bottom_right": 0, -- Right eye, bottom eyelid, right corner

            for corner in (
            "eye1_top_left","eye1_top_right",
            "eye1_bottom_left","eye1_bottom_right"
            "eye2_top_left","eye2_top_right",
            "eye2_bottom_left","eye2_bottom_right"
            ):
            
    },
EYE1 = LEFT EYE FROM VIEWER'S PERSPECTIVE
EYE2 = RIGHT EYE FROM VIEWER'S PERSPECTIVE
"""
FRAME_RATE = 60
FRAME_DURATION = 1.0 / FRAME_RATE

RED = "\033[91m"
GREEN = "\033[92m"
RESET = "\033[0m"


@dataclass
class EyeState:
    x: int = 10             # integer only
    y: int = 10             # integer only
    pupil: float = 1.0      # float, step of 0.01
    expression: str = "test2"  # string name only
    blink: float = 0.0      # 0.0 = open, 1.0 = fully closed

class EyeFrameComposer:
    def __init__(self, animator, expression_manager):
        self.expression_manager = expression_manager
        self.animator = animator
        self.state = EyeState()
        self._previous = EyeState()
        self.running = False
        self._dirty = True

    def set_gaze(self, x: int, y: int, pupil: float):
        self.state.x = round(x, 3)
        self.state.y = round(y, 3)
        self.state.pupil = round(pupil, 3)
        self._dirty = True

    async def set_expression(self, mood: str):
        print("----")
        print("EyeFrameComposer class:  async def set_expression(self, mood: str):")
        self.state.expression = mood
        self._dirty = True
        print(f"[EyeFrameComposer] self.state.expression = '{mood}'")
        print("[EyeFrameComposer] self._dirty = True")
        print("----")

    async def play_blink(self):
        # Signal “blink in progress”
        start_expression = self.state.expression
        print(f"[Blink] Starting blink with expression '{start_expression}'")
        await self.animator.animate_expression("closed", smooth=True, steps=6, delay=0.01)
        print("[Blink] Blink in progress...")
        await asyncio.sleep(0.1)
        await self.animator.animate_expression(start_expression, smooth=True, steps=6, delay=0.01)
        print("[Blink] Blink completed")
        self._dirty = True  # <-- THIS IS THE FIX
        print("[Blink] Re-flagged _dirty = True for next loop pass")
    
    async def start_idle_blink_loop(self):
        try:
            while True:
                # await asyncio.sleep(random.randint(8, 12))
                await asyncio.sleep(5)
                await self.play_blink()
        except asyncio.CancelledError:
            pass

    async def start_loop(self):
        self.running = True
        while self.running:
            if self._dirty or self.state != self._previous:
                # --- GAZE PHASE  ---
                await asyncio.to_thread(
                    self.animator.smooth_gaze,
                    x=self.state.x, y=self.state.y, pupil=self.state.pupil
                )

                # --- EXPRESSION PHASE (lock only around expression) ---
                print("[Composer] Triggering animate_expression")
                # async with self.animator.display_lock:
                await self.animator.animate_expression(self.state.expression)
                print("[Composer] animate_expression completed")

                # --- RENDER PHASE ---
                async with self.animator.expression_lock:
                    left_buf, right_buf = await asyncio.to_thread(
                        self.animator.drawer.render_gaze_frame,
                        self.state.x, self.state.y, self.state.pupil
                    )
                self.animator.last_buf = (left_buf, right_buf)

                # --- EYE‑LID MASK PHASE  ---
                try:
                    masked = await asyncio.to_thread(
                        self.animator.drawer.apply_lids,
                        (left_buf, right_buf),
                        lid_cfg = self.animator.drawer.lid_control.get_mask_config()
                    )
                except Exception:
                    masked = (left_buf, right_buf)

                # --- DISPLAY PHASE  ---
                await asyncio.to_thread(
                    self.animator.drawer.display, masked
                )

                # Save state snapshot
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

    def interp_pupil_transition(self, from_x, from_y, to_x, to_y, from_pupil, to_pupil, steps=8, delay=0.015):
        for i in range(1, steps + 1):
            interp_x = int(from_x + (to_x - from_x) * (i / steps))
            interp_y = int(from_y + (to_y - from_y) * (i / steps))
            raw_interp = from_pupil + (to_pupil - from_pupil) * (i / steps)
            interp_pupil = round(round(raw_interp / 0.01) * 0.01, 3)
            self.animator.draw_gaze(interp_x, interp_y, pupil=interp_pupil)
            time.sleep(delay)

    def interp_gaze_movement(self, to_x, to_y, to_pupil=1.0, steps=8, delay=0.015):
        state = self.animator.state
        self.interp_pupil_transition(
            from_x=state["x"],
            from_y=state["y"],
            to_x=to_x,
            to_y=to_y,
            from_pupil=state["pupil"],
            to_pupil=to_pupil,
            steps=steps,
            delay=delay
        )

    def translate_gaze_mode(self, mode):
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
        to_pupil = random.uniform(0.95, 1.15) if mode == "wander" else 1.0
        self.interp_gaze_movement(to_x, to_y, to_pupil)


class DrawEngine:
    def __init__(self, profile):
        self.profile = profile
        self.deformer = EyeDeformer(
            texture_name=profile.name,
            pupil_warp_strength=profile.pupil_warp_strength,
        )
        self.deformer.cache.warm_up_cache(kind="spherical", verbose=False)
        self.deformer.cache.warm_up_cache(kind="pupil", verbose=False)
        self.image = profile.image
        self.width = self.height = 160
        self.gaze_cache = {}
        self.lid_control = EyelidController()

    def render_gaze_frame(self, x_off, y_off, pupil_size=1.0):
        key = self._cache_key(x_off, y_off, pupil_size)
        if key not in self.gaze_cache:
            print(f"[DrawEngine] Generating new gaze frame for key: {key}")
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
        print("[DrawEngine] Buffers sent to both eyes.")
        # time.sleep(0.15)
    

    def _cache_key(self, x, y, pupil):
        lids = tuple(self.lid_control.get_mask_config().values())
        return (x, y, pupil, lids)

    def apply_lids(
        self,
        bufs: tuple[bytearray, bytearray],
        lid_cfg: dict
        ) -> tuple[bytearray, bytearray]:
        print(f"[apply_lids] Using lid cfg: {lid_cfg}")
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

        masked_left_img, masked_right_img = apply_eyelids((img1, img2), lid_cfg)

        left_buf  = self._get_buffer(masked_left_img)
        right_buf = self._get_buffer(masked_right_img)
        return left_buf, right_buf


class EyeAnimator:
    def __init__(self, profile):
        self.profile = profile
        self.state = {
            "x": 10,
            "y": 10,
            "pupil": 1.0
        }
        self.drawer = DrawEngine(profile)
        self.blinker = None  # <-- initially empty
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
        self.display_lock = asyncio.Lock()
        self.expression_lock = asyncio.Lock()

    # TEMP ALIAS for compatibility
    async def set_expression(self, *args, **kwargs):
        print("[WARN] set_expression() was called — redirecting to animate_expression()")
        await self.animate_expression(*args, **kwargs)

    def get_last_buf_safe(self):
        if self.last_buf is None:
            print("[Animator] last_buf was None, generating fallback gaze frame.")
            self.last_buf = self.drawer.render_gaze_frame(10, 10, 1.0)
        return self.last_buf

    def draw_gaze(self, x, y, pupil=1.0):
        self.state.update({"x": x, "y": y, "pupil": pupil})
        left_buf, right_buf = self.drawer.render_gaze_frame(x, y, pupil)
        self.drawer.display((left_buf, right_buf))
        self.last_buf = (left_buf, right_buf)

    def apply_gaze_mode(self, mode):
        self.interpolator.translate_gaze_mode(mode)

    def smooth_gaze(self, x, y, pupil=1.0):
        self.interpolator.interp_gaze_movement(x, y, pupil)

    async def animate_expression(self, mood: str, smooth: bool = False, steps=20, delay=0.02):
        async with self.expression_lock:
            print(f"[Animator] Starting expression transition: {mood}")
            do_smooth = smooth
            if do_smooth is None:
                # first time or resetting?
                do_smooth = (self.current_expression is not None
                            and self.current_expression != mood)

            if do_smooth:
                await self._smooth_expression(mood, steps=steps, delay=delay)
            else:
                await self._smooth_expression(mood, steps=1, delay=delay)

    async def _smooth_expression(self, mood: str, steps=20, delay=0.02):
        """
        Tween from the current expression corners to the new `mood`.
        """
        print(f"[Animator] Tweening to expression '{mood}'")

        expr_map = self.drawer.lid_control.expression_map
        target   = expr_map.get(mood)
        if not target:
            print(f"[EyeAnimator] Unknown expression '{mood}'")
            return
        
        missing = [k for k in (
            "eye1_top_left","eye1_top_right",
            "eye1_bottom_left","eye1_bottom_right",
            "eye2_top_left","eye2_top_right",
            "eye2_bottom_left","eye2_bottom_right"
        ) if k not in target]

        if missing:
            print(f"[ERROR] Expression '{mood}' is missing keys: {missing}")
            return

        async with self.display_lock:
            start_cfg = self.drawer.lid_control.lids.copy()
            for step in range(1, steps + 1):
                print(f"[Animator] Step {step}/{steps} — updating eyelid config")

                frac = step / steps
                interp_cfg = {}
                for corner in (
                    "eye1_top_left","eye1_top_right",
                    "eye1_bottom_left","eye1_bottom_right",
                    "eye2_top_left","eye2_top_right",
                    "eye2_bottom_left","eye2_bottom_right"
                    ):
                    s = start_cfg.get(corner, 0)
                    e = target.get(corner, s if s is not None else 0)
                    interp_cfg[corner] = int(s + (e - s) * frac)

                self.drawer.lid_control.lids.update(interp_cfg)

                # <-- same unpacking here
                left_buf, right_buf = self.drawer.render_gaze_frame(
                    self.state["x"],
                    self.state["y"],
                    pupil_size=self.state["pupil"]
                )
                self.drawer.display((left_buf, right_buf))
                self.last_buf = (left_buf, right_buf)

                self.drawer.gaze_cache.clear()
                await asyncio.sleep(delay)

            print(f"[Animator] Expression '{mood}' complete")
            self.current_expression = mood


class EyelidController:
    def __init__(self):
        # start with either hard-coded defaults or pull your "neutral" from the map:
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
        return lids


class EyeExpressionManager:
    def __init__(self, animator, multi_file=False):
        self.animator = animator
        self.multi_file = multi_file
        self.lid_control = EyelidController()
        self.expressions = self._load_expressions()

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
                    print(f"[ExpressionManager] Loaded expressions from single file.")
            except Exception as e:
                print(f"[ExpressionManager] Failed to load expressions: {e}")
        return expressions


class EyeCacheManager:
    def __init__(self, texture_name="default"):
        self.base_dir = EYE_CACHE_PATH
        self.texture_name = texture_name
        self.pupil_dir = self.base_dir / texture_name / "pupil"
        self.spherical_dir = self.base_dir / texture_name / "spherical"
        self.pupil_dir.mkdir(parents=True, exist_ok=True)
        self.spherical_dir.mkdir(parents=True, exist_ok=True)

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
        ext = ".npz" if kind == "spherical" else ".npy"
        file_path = (self.pupil_dir if kind == "pupil" else self.spherical_dir) / (key + ext)

        if not file_path.exists():
            return None

        try:
            if kind == "spherical":
                # load both map_x and map_y
                with np.load(file_path, allow_pickle=True) as data:
                    return data["map_x"], data["map_y"]
            else:
                # load a simple array
                return np.load(file_path, allow_pickle=True)
        except Exception as e:
            # something’s corrupted: delete it and fall back
            try:
                file_path.unlink()
            except Exception:
                pass
            return None


    def exists(self, key_dict, kind="pupil"):
        return self._get_path(key_dict, kind).exists()

    def warm_up_cache(self, kind="pupil", verbose=False):
        ext = ".npz" if kind == "spherical" else ".npy"
        cache_dir = self.pupil_dir if kind == "pupil" else self.spherical_dir
        log_file = self.base_dir / f"bad_cache_{kind}.log"

        loaded = 0
        skipped = 0
        deleted = 0
        errors = []

        # if verbose:
        #     print(f"[Cache Warm-Up] Preloading '{kind}' maps from {cache_dir}...")

        for file in cache_dir.glob(f"*{ext}"):
            try:
                if ext == ".npy":
                    data = np.load(file)
                    if data is None or not hasattr(data, 'shape'):
                        raise ValueError("Empty or malformed .npy")
                else:
                    with np.load(file) as data:
                        if "map_x" not in data or "map_y" not in data:
                            raise ValueError("Missing keys in .npz")

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

        # Write log
        if errors:
            with open(log_file, "a") as log:
                log.write(f"\n[Run at {time.ctime()}] Errors in {kind} cache:\n")
                for e in errors:
                    log.write(f"- {e}\n")

        if verbose:
            print(f"[Cache Warm-Up] Complete. Loaded: {loaded}, Deleted: {deleted}, Errors Logged: {len(errors)}")


        def __getattr__(self, name):
            if name == "texture_cache_dir":
                raise AttributeError("Use pupil_dir or spherical_dir instead of texture_cache_dir.")


class EyeDeformer:
    def __init__(
            self,
            output_size=160,
            pupil_warp_strength=1.0,
            texture_name="default",
            verbose=False
            ):
        self.cache = EyeCacheManager(texture_name=texture_name)
        self.output_size = output_size
        self.warp_strength = pupil_warp_strength
        self.verbose = verbose

    def generate_eye_frame(
        self,
        source_img,
        pupil_size=1.0,
        x_off=10,
        y_off=10,
        iris_radius=42,
        perspective_shift=0.02,
        output_size=160
    ):
        pupil_maps = self.get_or_generate_pupil_warp_map(
            pupil_size=pupil_size,
            iris_radius=iris_radius,
        )
        warped_pupil = self.apply_pupil_warp(source_img, *pupil_maps)

        gaze_aligned = self.crop_to_display(warped_pupil, x_off, y_off, output_size)

        final_img = self.apply_spherical_warp(
            gaze_aligned,
            x_off=x_off,
            y_off=y_off,
            strength=perspective_shift
        )

        return Image.fromarray(final_img.astype(np.uint8), mode='RGB')

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

        yy, xx = np.meshgrid(np.arange(h), np.arange(w), indexing='xy')
        dx = (xx - center_x) / center_x
        dy = (yy - center_y) / center_y
        r = np.sqrt(dx**2 + dy**2)
        z = np.sqrt(1.0 - np.clip(r**2, 0, 1))

        shift_scale = strength / 2
        dx += norm_x * shift_scale * z
        dy += norm_y * shift_scale * z

        map_x = (dx * center_x + center_x).astype(np.float32)
        map_y = (dy * center_y + center_y).astype(np.float32)

        self.cache.save_map(key_dict, (map_x, map_y), kind="spherical")
        return map_x, map_y

    def apply_spherical_warp(self, image, x_off=10, y_off=10, strength=0.03):
        map_x, map_y = self.get_or_generate_spherical_map(x_off, y_off, strength)
        return cv2.remap(image, map_x, map_y, interpolation=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)

    def get_or_generate_pupil_warp_map(self, pupil_size, iris_radius):
        key_dict = {
            "pupil_size":    round(float(pupil_size), 3),
            "iris_radius":   iris_radius,
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

    def crop_to_display(self, image, x_off, y_off, output_size=160):
        h, w = image.shape[:2]
        center_x = w // 2
        center_y = h // 2
        crop_x = center_x - output_size // 2 + (x_off - 10)
        crop_y = center_y - output_size // 2 + (y_off - 10)
        crop_x = np.clip(crop_x, 0, w - output_size)
        crop_y = np.clip(crop_y, 0, h - output_size)
        crop_x = int(crop_x)
        crop_y = int(crop_y)
        output_size = int(output_size)
        return image[crop_y:crop_y + output_size, crop_x:crop_x + output_size]


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


def apply_eyelids(imgs: tuple[Image.Image, Image.Image], cfg: dict) -> tuple[Image.Image, Image.Image]:
    """
    Mask out each eyelid corner independently for both eyes.
    cfg must have keys:
      'eye1_top_left', 'eye1_top_right', 'eye1_bottom_left', 'eye1_bottom_right',
      'eye2_top_left', 'eye2_top_right', 'eye2_bottom_left', 'eye2_bottom_right'.
    Returns (left_eye_img, right_eye_img).
    """
    img1, img2 = imgs
    w, h = img1.size

    def make_mask(tl, tr, bl, br):
        m = Image.new("L", (w, h), 255)
        d = ImageDraw.Draw(m)
        # top lid
        d.polygon([(0,0),(w,0),(w, tr),(0, tl)], fill=0)
        # bottom lid
        d.polygon([(0,h),(w,h),(w, h - br),(0, h - bl)], fill=0)
        return m

    # build masks for each eye
    m1 = make_mask(cfg["eye1_top_left"], cfg["eye1_top_right"],
                   cfg["eye1_bottom_left"], cfg["eye1_bottom_right"])
    m2 = make_mask(cfg["eye2_top_left"], cfg["eye2_top_right"],
                   cfg["eye2_bottom_left"], cfg["eye2_bottom_right"])

    arr1 = np.array(img1)
    arr2 = np.array(img2)
    out1 = Image.fromarray(arr1 * (np.array(m1)[:, :, None] // 255))
    out2 = Image.fromarray(arr2 * (np.array(m2)[:, :, None] // 255))
    return out1, out2
