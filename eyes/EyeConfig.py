from helpers.global_config import EYE_ASSETS_PATH
from PIL import Image
import json


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
        self.max_gaze_range = config.get("max_gaze_range", 10)
        self.close_speed = config.get("close_speed", 0.01)
        self.open_speed = config.get("open_speed", 0.03)
        self.hold = config.get("hold", 0.08)
        self.animation_style = config.get("animation_style", "default")
        self.expression_profile = config.get("expression_profile", "default")
        self.use_case = config.get("use_case", "default")

    @classmethod
    def load_eye_profile(cls, name):
        config_path = EYE_ASSETS_PATH / f"{name}.json"
        image_path = EYE_ASSETS_PATH / f"{name}.png"

        if not config_path.exists():
            raise FileNotFoundError(f"No config for {name} at {config_path}")
        if not image_path.exists():
            raise FileNotFoundError(f"No image for {name} at {image_path}")

        with open(config_path, "r") as f:
            config = json.load(f)

        image = Image.open(image_path).convert("RGB")
        return cls(name, config_path, config, image)
    