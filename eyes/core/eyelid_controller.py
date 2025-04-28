from helpers.global_config import EYE_EXPRESSIONS_PATH, EYE_EXPRESSIONS_FILE
import json
expressionconfig_path = EYE_EXPRESSIONS_PATH / EYE_EXPRESSIONS_FILE
if not expressionconfig_path.exists():
    raise FileNotFoundError(f"[EyeLoader] No profile named '{EYE_EXPRESSIONS_FILE}' in {EYE_EXPRESSIONS_PATH}/")
with open(expressionconfig_path, "r") as f:
    expression_map = json.load(f)
"""
eye_expressions.json schema:

Each expression dict may contain:
    "test": {
        "top": 0,               -- LEGACY VALUE.  assumes left and right corners are same value
        "bottom": 0,            -- LEGACY VALUE.  assumes left and right corners are same value
        "left": 0,              -- LEGACY VALUE.  assumes top and bottom corners are same value 
        "right": 0,             -- LEGACY VALUE.  assumes top and bottom corners are same value
        "eye1_top_left": 0,     -- Left eye, top eyelid, left corner
        "eye1_top_right": 0,    -- Left eye, top eyelid, right corner
        "eye1_bottom_left": 0,  -- Left eye, bottom eyelid, left corner 
        "eye1_bottom_right": 0, -- Left eye, bottom eyelid, right corner
        "eye2_top_left": 0,     -- Right eye, top eyelid, left corner
        "eye2_top_right": 0,    -- Right eye, top eyelid, right corner
        "eye2_bottom_left": 0,  -- Right eye, bottom eyelid, left corner
        "eye2_bottom_right": 0, -- Right eye, bottom eyelid, right corner
        "gaze_x": 10,           -- X coordinate of centered offset gaze (0-20)
        "gaze_y": 10,           -- Y coordinate of centered offset gaze (0-20)
        "pupil_size": 1.0       -- Pupil size (typical range: 0.9-1.2) default value = 1.0
    },
EYE1 = LEFT EYE FROM VIEWER'S PERSPECTIVE
EYE2 = RIGHT EYE FROM VIEWER'S PERSPECTIVE
Example “test” entry:
  “test”: {
      “lid_top_left”: 0,     # fully open
      “lid_top_right”: 0,    # fully open
      “lid_bottom_left”: 0,  # fully up
      “lid_bottom_right”: 0, # fully up
      “gaze_x”: 10,          # centre
      “gaze_y”: 10,          # centre
      “pupil_size”: 1.0      # normal
  }
"""


class EyelidController:
    def __init__(self):
        # start with either hard-coded defaults or pull your "neutral" from the map:
        neutral = expression_map.get("neutral", {})
        # ensure all four corners exist
        self.lids = {
            "top_left":  neutral.get("lid_top_left",  36),
            "top_right": neutral.get("lid_top_right", 36),
            "bottom_left":  neutral.get("lid_bottom_left",  40),
            "bottom_right": neutral.get("lid_bottom_right", 40),
        }
        self.expression_map = expression_map

    def set_expression(self, name):
        exp = self.expression_map.get(name)
        if not exp:
            print(f"[EyelidController] Unknown expression: {name}")
            return

        # Allow both symmetric or asymmetric key sets
        self.lids["top"] = exp.get("top", self.lids["top"])
        self.lids["bottom"] = exp.get("bottom", self.lids["bottom"])
        self.lids["left"] = exp.get("left", self.lids["left"])
        self.lids["right"] = exp.get("right", self.lids["right"])
        if "top_left" in exp:
            self.lids["top_left"] = exp["top_left"]
        if "top_right" in exp:
            self.lids["top_right"] = exp["top_right"]

    def get_mask_config(self):
        # start with exactly what you've set on self.lids
        cfg = self.lids.copy()

        # only calculate legacy keys if JSON didn't already give them
        if "top" not in cfg:
            cfg["top"] = min(cfg["top_left"], cfg["top_right"])
        if "bottom" not in cfg:
            cfg["bottom"] = max(cfg["bottom_left"], cfg["bottom_right"])
        if "left" not in cfg:
            cfg["left"] = min(cfg["top_left"], cfg["bottom_left"])
        if "right" not in cfg:
            cfg["right"] = max(cfg["top_right"], cfg["bottom_right"])

        return cfg