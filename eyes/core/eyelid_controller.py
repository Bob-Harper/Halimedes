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
        "eye1_top_left": 0,     -- Left eye, top eyelid, left corner
        "eye1_top_right": 0,    -- Left eye, top eyelid, right corner
        "eye1_bottom_left": 0,  -- Left eye, bottom eyelid, left corner 
        "eye1_bottom_right": 0, -- Left eye, bottom eyelid, right corner
        "eye2_top_left": 0,     -- Right eye, top eyelid, left corner
        "eye2_top_right": 0,    -- Right eye, top eyelid, right corner
        "eye2_bottom_left": 0,  -- Right eye, bottom eyelid, left corner
        "eye2_bottom_right": 0, -- Right eye, bottom eyelid, right corner

            for corner in (
            "eye1_top_left","eye1_top_right",
            "eye1_bottom_left","eye1_bottom_right"
            "eye2_top_left","eye2_top_right",
            "eye2_bottom_left","eye2_bottom_right"
            ):
            
    },
EYE1 = LEFT EYE FROM VIEWER'S PERSPECTIVE
EYE2 = RIGHT EYE FROM VIEWER'S PERSPECTIVE
"""


class EyelidController:
    def __init__(self):
        # start with either hard-coded defaults or pull your "neutral" from the map:
        neutral = expression_map.get("neutral", {})
        # ensure all four corners exist
        self.lids = {
            "eye1_top_left":        neutral.get("eye1_top_left",    36),
            "eye1_top_right":       neutral.get("eye1_top_right",   40),
            "eye1_bottom_left":     neutral.get("eye1_bottom_left",  0),
            "eye1_bottom_right":    neutral.get("eye1_bottom_right", 0),
            "eye2_top_left":        neutral.get("eye2_top_left",    36),
            "eye2_top_right":       neutral.get("eye2_top_right",   36),
            "eye2_bottom_left":     neutral.get("eye2_bottom_left",  40),
            "eye2_bottom_right":    neutral.get("eye2_bottom_right", 40),
        }
        self.expression_map = expression_map

    def set_expression(self, name: str):
        print(f"[LidController] Switching to expression: {name}")
        exp = self.expression_map.get(name)
        if not exp:
            print(f"[EyelidController] Unknown expression: {name}")
            return
        # copy over only the keys we care about
        for corner in (
            "eye1_top_left","eye1_top_right",
            "eye1_bottom_left","eye1_bottom_right",
            "eye2_top_left","eye2_top_right",
            "eye2_bottom_left","eye2_bottom_right"
        ):
            if corner in exp:
                self.lids[corner] = exp[corner]

    def get_mask_config(self) -> dict:
        lids = self.lids
        return lids
