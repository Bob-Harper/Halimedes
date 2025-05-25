from eyes.eye_frame_composer import load_eye_profile, DrawEngine

profile = load_eye_profile("vector03")
engine = DrawEngine(profile)
print("Rendering test gaze...")
left, right = engine.render_gaze_frame(10, 10, 1.0)
print("Success. Buffer types:", type(left), type(right))
