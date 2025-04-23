class EyelidController:
    def __init__(self):
        self.lids = {
            "top": 36,
            "bottom": 40,
            "left": 0,
            "right": 0
        }

        self.expression_map = {
            "neutral":  {"top": 36, "bottom": 40, "left": 0,  "right": 0},
            "happy":    {"top": 28, "bottom": 50, "left": 0,  "right": 0},
            "sad":      {"top": 55, "bottom": 20, "left": 0,  "right": 0},
            "angry":    {"top": 65, "bottom": 15, "left": 4,  "right": 4},
            "focused":  {"top": 48, "bottom": 48, "left": 0,  "right": 0},
            "skeptical":{"top_left": 32, "top_right": 60, "bottom": 36, "left": 4, "right": 0},
            "surprised":{"top": 18, "bottom": 60, "left": 0,  "right": 0},
            "asleep":   {"top": 80, "bottom": 80, "left": 0,  "right": 0}
        }

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
        # Returns the current lid values for masking
        return self.lids
