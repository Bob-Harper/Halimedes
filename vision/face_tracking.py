# vision/face_tracking.py

import time, asyncio
from vilib import Vilib

class FaceTracker:
    def __init__(self, animator,
                 clamp_x=(100,540), clamp_y=(100,380),
                 gaze_range=20, timeout=0.75,
                 visible_pupil=1.15, hidden_pupil=0.8):
        self.animator = animator
        self.min_x, self.max_x = clamp_x
        self.min_y, self.max_y = clamp_y
        self.range_x = self.max_x - self.min_x
        self.range_y = self.max_y - self.min_y
        self.gaze_range = gaze_range
        self.timeout = timeout
        self.face_visible = visible_pupil
        self.face_invisible = hidden_pupil

        self.last_seen = time.time()
        # start looking straight ahead
        centered = gaze_range / 2
        self.last_coords = (centered, centered)

    def map_face_to_gaze(self, face_x, face_y):
        # clamp to your active detection window
        face_x = max(100, min(540, face_x))
        face_y = max(100, min(380, face_y))

        # normalize to 0.0–1.0
        norm_x = (face_x - 100) / 440  # 540–100 = 440
        norm_y = (face_y - 100) / 280  # 380–100 = 280

        # scale into your gaze-range (0–20)
        raw_x = norm_x * 20
        raw_y = norm_y * 20

        # rotate + flip 90° (same as before)
        rot_x = raw_y
        rot_y = 20 - raw_x

        # mirror horizontally AND vertically
        x_off = 20 - rot_x
        y_off = 20 - rot_y

        return x_off, y_off

    async def track(self):
        # init camera & face-detect
        Vilib.camera_start(vflip=False, hflip=False)
        Vilib.face_detect_switch(True)

        try:
            while True:
                x_off, y_off = self.last_coords
                pupil = self.face_invisible

                if Vilib.face_obj_parameter.get("n", 0) > 0:
                    fx = Vilib.detect_obj_parameter["human_x"]
                    fy = Vilib.detect_obj_parameter["human_y"]
                    x_off, y_off = self.map_face_to_gaze(fx, fy)
                    self.last_seen = time.time()
                    self.last_coords = (x_off, y_off)
                    pupil = self.face_visible
                else:
                    if time.time() - self.last_seen < self.timeout:
                        pupil = self.face_visible

                self.animator.smooth_gaze(x_off, y_off, pupil=pupil)
                await asyncio.sleep(0.2)
        except asyncio.CancelledError:
            # (optional) clean up or just swallow
            pass
        
        finally:
            Vilib.camera_close()

