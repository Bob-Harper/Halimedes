def main(texture_name="vector03", pupil=1.0):
    import numpy as np
    from eyes.eye_frame_composer import load_eye_profile, DrawEngine
    from eyes.eye_frame_composer import GazeFrameCacheManager

    profile = load_eye_profile(texture_name)
    engine = DrawEngine(profile)
    cache = GazeFrameCacheManager(texture_name)

    total = 0
    baked = 0

    for x in np.arange(0, 20.01, 0.2):
        for y in np.arange(0, 20.01, 0.2):
            x_q = round(x, 2)
            y_q = round(y, 2)
            key = (x_q, y_q, pupil)

            if not cache.load_frame(*key):
                engine.render_gaze_frame(x_q, y_q, pupil)
                baked += 1
            total += 1

            if total % 100 == 0 or baked % 50 == 0:
                print(f"[Bake] Progress: {baked}/{total} frames baked")

    print(f"[Bake] DONE. Baked {baked} out of {total} possible gaze frames.")

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Bake gaze frames for eye profile.")
    parser.add_argument(
        "--texture_name",
        type=str,
        default="vector03",
        help="Name of the eye texture profile to use.",
    )
    parser.add_argument(
        "--pupil",
        type=float,
        default=1.0,
        help="Pupil size for the gaze frames.",
    )

    args = parser.parse_args()
    main(args.texture_name, args.pupil)
