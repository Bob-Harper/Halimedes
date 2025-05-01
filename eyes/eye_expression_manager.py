import json
import os
import time

class EyeExpressionManager:
    def __init__(self, animator, multi_file=False):
        self.animator = animator
        self.multi_file = multi_file
        self.expressions = self._load_expressions()

    def _load_expressions(self):
        expressions = {}
        base_dir = os.path.dirname(__file__)
        expr_path = os.path.join(base_dir, "eye_expressions.json")

        if self.multi_file:
            for file in os.listdir(base_dir):
                if file.endswith(".json") and file != "eye_expressions.json":
                    path = os.path.join(base_dir, file)
                    try:
                        with open(path, "r") as f:
                            name = os.path.splitext(file)[0]
                            expressions[name] = json.load(f)
                            print(f"[ExpressionManager] Loaded '{name}' from file.")
                    except Exception as e:
                        print(f"[ExpressionManager] Failed to load {file}: {e}")
        else:
            try:
                with open(expr_path, "r") as f:
                    expressions = json.load(f)
                    print(f"[ExpressionManager] Loaded expressions from single file.")
            except Exception as e:
                print(f"[ExpressionManager] Failed to load expressions: {e}")
        return expressions

    def run(self, name):
        config = self.expressions.get(name)
        if not config:
            print(f"[ExpressionManager] Unknown expression: '{name}'")
            return

        try:
            # Apply eyelid positions
            for lid_key in [
                'lid_top_left', 'lid_top_right',
                'lid_bottom_left', 'lid_bottom_right'
            ]:
                if lid_key in config:
                    self.animator.set_lid_position(lid_key, config[lid_key])

            # Apply gaze
            x = config.get("gaze_x")
            y = config.get("gaze_y")
            pupil = config.get("pupil_size", 1.0)
            if x is not None and y is not None:
                self.animator.draw_gaze(x, y, pupil)

        except Exception as e:
            print(f"[ExpressionManager] Error applying '{name}': {e}")
