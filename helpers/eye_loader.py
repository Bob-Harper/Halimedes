# eye_loader.py
import json
from pathlib import Path
from PIL import Image

class EyeProfile:
    def __init__(self, name, config, image):
        self.name = name
        self.image = image
        self.texture_path = config["image_path"]
        self.sclera_radius = config.get("sclera_radius", 85)
        self.pupil_min = config.get("pupil_min", 0.5)
        self.pupil_max = config.get("pupil_max", 1.5)
        self.directional = config.get("directional", False)

def load_eye_profile(profile_name):
    config_path = Path(f"/home/msutt/hal/eyes/{profile_name}.json")
    if not config_path.exists():
        raise FileNotFoundError(f"No profile named '{profile_name}' in eyes/ directory")

    with open(config_path, "r") as f:
        config = json.load(f)

    texture_path = Path(config["image_path"])
    if not texture_path.exists():
        raise FileNotFoundError(f"Texture file '{texture_path}' not found.")

    img = Image.open(texture_path).convert('RGB')

    # Resize + rotate if necessary
    if img.width != img.height:
        print(f"[WARNING] Eye texture is not square ({img.width}x{img.height})")
    if img.width != 180:
        img = img.resize((180, 180), resample=Image.LANCZOS)
    if config.get("directional", False):
        img = img.rotate(90, expand=True)

    return EyeProfile(profile_name, config, img)
