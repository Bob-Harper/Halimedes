
import json
import argparse
from pathlib import Path
import numpy as np
from eyes.core.eye_deform import EyeDeformer


def load_profile_config(config_path):
    with open(config_path, "r") as f:
        return json.load(f)


def precompute_all_maps_from_config(config_path):
    profile = load_profile_config(config_path)
    texture_name = Path(config_path).stem

    pupil_min = profile.get("pupil_min", 0.95)
    pupil_max = profile.get("pupil_max", 1.15)
    pupil_step = 0.05
    iris_radius = profile.get("iris_radius", 44)
    perspective_shift = profile.get("perspective_shift", 0.03)

    print(f"[Precompute] Profile: {texture_name}")
    print(f"  pupil range: {pupil_min} to {pupil_max}")
    print(f"  iris_radius: {iris_radius}")
    print(f"  perspective shift: {perspective_shift}")

    deformer = EyeDeformer(texture_name=texture_name, verbose=True)

    for pupil_size in np.arange(pupil_min, pupil_max + pupil_step, pupil_step):
        deformer.get_or_generate_pupil_warp_map(
            pupil_size=round(pupil_size, 3),
            iris_radius=iris_radius
        )

    for x in range(20):
        for y in range(20):
            deformer.get_or_generate_spherical_map(
                x_off=x,
                y_off=y,
                strength=perspective_shift
            )

    print("[Precompute] Done.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("config", help="Path to eye profile config JSON")
    args = parser.parse_args()
    precompute_all_maps_from_config(args.config)
