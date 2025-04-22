import json
from pathlib import Path

DEFAULT_CONFIG = {
    "sclera_size": 80,
    "iris_radius": 42,
    "pupil_radius": 20,
    "feather_width": 8,
    "directional": True,
    "pupil_min": 0.6,
    "pupil_max": 1.4,
    "eyelid_top": 16,
    "eyelid_bottom": 16,
    "eyelid_left": 0,
    "eyelid_right": 0,
    "perspective_skew": 0.01,
    "perspective_scale": 0.15,
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
            # Update missing keys
            updated = {**config, **existing}
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
    upgrade_or_create_profiles("eyes/images")
