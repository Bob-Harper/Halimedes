class Frame:
    def __init__(self, legs, body=None):
        self.legs = legs        # dict: name -> [x,y,z] in world space (mm)
        self.body = body or {}  # roll/pitch/yaw/height

class Gait:
    def __init__(self, name, frames, loop=True):
        self.name = name
        self.frames = [Frame(f) if isinstance(f, dict) else f for f in frames]
        self.loop = loop

class GaitEngine:
    def __init__(self, ik, state):
        self.ik = ik
        self.state = state  # HalCrawler instance
        self.current_gait: Gait | None = None
        self.current_frame_idx = 0
        self.diagonal_phase = 0

    def start_gait(self, gait):
        if not gait.frames:
            return
        self.current_gait = gait
        self.current_frame_idx = 0

    def step(self):
        if not self.current_gait:
            return

        frame = self.current_gait.frames[self.current_frame_idx]

        if self.diagonal_phase == 1:
            frame = self._flip_diagonal(frame)

        self._apply_frame(frame)
        self._advance()

    def _apply_frame(self, frame):
        # 1. Standardize formatting into structural targets
        body_aligned_targets = {}
        for leg_name, xyz in frame.legs.items():
            body_aligned_targets[leg_name] = {
                "dx": xyz[0],
                "dy": xyz[1],
                "dz": xyz[2]
            }

        # 2. Extract live orientation payload directly out of the state layer
        imu_data = {"pitch": 0.0, "roll": 0.0}
        if hasattr(self.state, 'sensor_imu') and self.state.sensor_imu:
            imu_data = self.state.sensor_imu.get_pitch_roll()

        # 3. Safely pass down to working level and speed controls.  Speed in this context is Governer smoothing rate
        self.state.execute_local_step(body_aligned_targets, speed=20, imu_data=imu_data)

    def _advance(self):
        if not self.current_gait:
            return

        self.current_frame_idx += 1
        if self.current_frame_idx >= len(self.current_gait.frames):
            if self.current_gait.loop:
                self.current_frame_idx = 0
                self.diagonal_phase = 1 - self.diagonal_phase
            else:
                self.current_frame_idx = len(self.current_gait.frames) - 1

    def _flip_diagonal(self, frame):
        mapping = {"LF": "RR", "RR": "LF", "RF": "LR", "LR": "RF"}
        flipped_legs = {}
        for leg_name, xyz in frame.legs.items():
            target_leg = mapping[leg_name]
            flipped_legs[target_leg] = [-xyz[0], -xyz[1], xyz[2]]
        return Frame(flipped_legs, frame.body)


Z_STANCE = -40   # body height (tune later)
STEP_X   = 25    # forward stride
LIFT_Z   = 35    # foot lift height
SHIFT_X  = 25    # body advance per cycle


STANCE = {
    "LF": [65,  85, Z_STANCE],
    "RF": [65, -85, Z_STANCE],
    "RR": [-65, -85, Z_STANCE],
    "LR": [-65,  85, Z_STANCE],
}

walk_forward_frames = [
    # 1: lift + start swing RF
    {
        "LF": [65,  85, Z_STANCE],
        "RF": [65 + STEP_X/2, -85, Z_STANCE + LIFT_Z],
        "RR": [-65, -85, Z_STANCE],
        "LR": [-65,  85, Z_STANCE],
    },
    # 2: full swing RF
    {
        "LF": [65,  85, Z_STANCE],
        "RF": [65 + STEP_X, -85, Z_STANCE + LIFT_Z],
        "RR": [-65, -85, Z_STANCE],
        "LR": [-65,  85, Z_STANCE],
    },
    # 3: place RF
    {
        "LF": [65,  85, Z_STANCE],
        "RF": [65 + STEP_X, -85, Z_STANCE],
        "RR": [-65, -85, Z_STANCE],
        "LR": [-65,  85, Z_STANCE],
    },
    # 4: shift body forward (all feet relative)
    {
        "LF": [65 + SHIFT_X,  85, Z_STANCE],
        "RF": [65 + STEP_X + SHIFT_X, -85, Z_STANCE],
        "RR": [-65 + SHIFT_X, -85, Z_STANCE],
        "LR": [-65 + SHIFT_X,  85, Z_STANCE],
    },
    # 5: lift + swing RR
    {
        "LF": [65 + SHIFT_X,  85, Z_STANCE],
        "RF": [65 + STEP_X + SHIFT_X, -85, Z_STANCE],
        "RR": [-65 + SHIFT_X/2, -85, Z_STANCE + LIFT_Z],
        "LR": [-65 + SHIFT_X,  85, Z_STANCE],
    },
    # 6: place RR forward
    {
        "LF": [65 + SHIFT_X,  85, Z_STANCE],
        "RF": [65 + STEP_X + SHIFT_X, -85, Z_STANCE],
        "RR": [-65 + SHIFT_X + STEP_X, -85, Z_STANCE],
        "LR": [-65 + SHIFT_X,  85, Z_STANCE],
    },
    # 7: reset stance (optional, or next cycle starts here)
    {
        "LF": [65 + SHIFT_X,  85, Z_STANCE],
        "RF": [65 + STEP_X + SHIFT_X, -85, Z_STANCE],
        "RR": [-65 + SHIFT_X + STEP_X, -85, Z_STANCE],
        "LR": [-65 + SHIFT_X,  85, Z_STANCE],
    },
]
