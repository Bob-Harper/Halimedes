# no imports yet!

def map_face_to_gaze(face_x, face_y):
    """ Map Vilib face detection (0–320, 0–240) to gaze range (0–20, 0–20) """
    # Normalize 0–320 to 0–20
    x_off = int((face_x / 320.0) * 20)
    y_off = int((face_y / 240.0) * 20)

    # Clamp values just in case
    x_off = max(0, min(20, x_off))
    y_off = max(0, min(20, y_off))

    return x_off, y_off
