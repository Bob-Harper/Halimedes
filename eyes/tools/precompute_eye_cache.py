
import numpy as np
from eyes.EyeDeformer import EyeDeformer

def precompute_all_maps(
    texture_name="default",
    pupil_range=(0.6, 1.4),
    pupil_step=0.05,
    gaze_range=(0, 20),
    spherical_strength=0.03
):
    print(f"[Precompute] Starting precompute for texture '{texture_name}'")

    deformer = EyeDeformer(texture_name=texture_name, verbose=True)

    print("[Precompute] Caching pupil warp maps...")
    for pupil_scale in np.arange(pupil_range[0], pupil_range[1] + pupil_step, pupil_step):
        deformer.get_or_generate_pupil_warp_map(
            pupil_scale=round(pupil_scale, 3),
            iris_radius=42
        )

    print("[Precompute] Caching spherical warp maps...")
    for x in range(gaze_range[0], gaze_range[1]):
        for y in range(gaze_range[0], gaze_range[1]):
            deformer.get_or_generate_spherical_map(
                x_off=x,
                y_off=y,
                strength=spherical_strength
            )

    print("[Precompute] Complete!")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--texture", default="default", help="Texture profile name")
    parser.add_argument("--pmin", type=float, default=0.6, help="Min pupil size")
    parser.add_argument("--pmax", type=float, default=1.4, help="Max pupil size")
    parser.add_argument("--step", type=float, default=0.05, help="Pupil size step")
    parser.add_argument("--gsize", type=int, default=20, help="Gaze grid size (NxN)")
    parser.add_argument("--strength", type=float, default=0.03, help="Spherical warp strength")
    args = parser.parse_args()

    precompute_all_maps(
        texture_name=args.texture,
        pupil_range=(args.pmin, args.pmax),
        pupil_step=args.step,
        gaze_range=(0, args.gsize),
        spherical_strength=args.strength
    )
