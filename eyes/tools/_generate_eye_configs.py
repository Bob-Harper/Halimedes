
import json
from pathlib import Path

DEFAULT_CONFIG = {
    "iris_radius": 42,
    "directional": True,
    "pupil_min": 0.6,
    "pupil_max": 1.4,
    "perspective_shift": 0.02,
    "x_off": 10,
    "y_off": 10,
    "close_speed": 0.01,
    "open_speed": 0.03,
    "hold": 0.08,
    "animation_style": "default",
    "expression_profile": "default",
    "use_case": "passive"
}

# Fields to be removed from each JSON profile, 
FIELDS_TO_REMOVE = ["pupil_radius", "feather_width", "eyelid_top", "eyelid_bottom", "eyelid_left", "eyelid_right"
                    "perspective_skew", "perspective_scale"]

def upgrade_or_create_profiles(images_dir: str, json_dir: str = None):
    img_path = Path(images_dir).resolve()
    json_path = Path(json_dir or images_dir).resolve()

    for img_file in img_path.glob("*.png"):
        name = img_file.stem
        profile_file = json_path / f"{name}.json"

        config = DEFAULT_CONFIG.copy()
        config["image_path"] = str(img_file)

        if profile_file.exists():
            with open(profile_file) as f:
                existing = json.load(f)
            updated = {**config, **existing}

            # Remove unwanted fields
            for field in FIELDS_TO_REMOVE:
                if field in updated:
                    print(f"[STRIP] Removing '{field}' from {profile_file.name}")
                    updated.pop(field)

            if updated != existing:
                print(f"[UPDATE] {profile_file.name}")
                with open(profile_file, "w") as f:
                    json.dump(updated, f, indent=2)
            else:
                print(f"[SKIP]   {profile_file.name} already up-to-date")
        else:
            print(f"[CREATE] {profile_file.name}")
            with open(profile_file, "w") as f:
                json.dump(config, f, indent=2)

if __name__ == "__main__":
    upgrade_or_create_profiles("/home/msutt/hal/eyes/eye_assets")