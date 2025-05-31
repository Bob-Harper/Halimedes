import json
import os
from pathlib import Path
import numpy as np
from eyes.EyeDeformer import EyeDeformer


def load_profile_config(config_path):
    with open(config_path, "r") as f:
        return json.load(f)


def precompute_all_maps_from_config(config_path):
    profile = load_profile_config(config_path)
    texture_name = Path(config_path).stem

    pupil_scale_min = profile.get("pupil_scale_min", 0.95)
    pupil_scale_max = profile.get("pupil_scale_max", 1.15)
    pupil_step = 0.01
    iris_radius = profile.get("iris_radius", 44)
    gaze_perspective_shift = profile.get("gaze_perspective_shift", 0.03)

    print(f"[Precompute] Profile: {texture_name}")
    print(f"  pupil range: {pupil_scale_min} to {pupil_scale_max}")
    print(f"  iris_radius: {iris_radius}")
    print(f"  perspective shift: {gaze_perspective_shift}")

    deformer = EyeDeformer(texture_name=texture_name, verbose=True)

    for pupil_scale in np.arange(pupil_scale_min, pupil_scale_max + pupil_step, pupil_step):
        deformer.get_or_generate_pupil_warp_map(
            pupil_scale=round(pupil_scale, 3),
            iris_radius=iris_radius
        )

    for x in range(20):
        for y in range(20):
            deformer.get_or_generate_spherical_map(
                x_off=x,
                y_off=y,
                strength=gaze_perspective_shift
            )

    print("[Precompute] Done.")


if __name__ == "__main__":
    eye_assets_directory = '/home/msutt/hal/eyes/eye_assets'
    
    # Get all .json files in the directory
    json_files = [f for f in os.listdir(eye_assets_directory) if f.endswith('.json')]
    
    for json_file in json_files:
        json_path = os.path.join(eye_assets_directory, json_file)
        print(f"Processing {json_file}...")
        precompute_all_maps_from_config(json_path)
