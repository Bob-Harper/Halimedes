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

    def smooth_transition_expression(self, mood, steps=20, delay=0.02):
        """Smoothly interpolate to a new expression over multiple frames."""
        old_lids = self.drawer.lid_control.get_mask_config()
        self.drawer.lid_control.set_expression(mood)
        new_lids = self.drawer.lid_control.get_mask_config()

        # Revert to old to start transition
        self.drawer.lid_control.lids.update(old_lids)

        # Stepwise interpolation
        for step in range(1, steps + 1):
            intermediate = {}
            for key in old_lids:
                start = old_lids.get(key, 0)
                end = new_lids.get(key, 0)
                intermediate[key] = int(start + (end - start) * (step / steps))
            self.drawer.lid_control.lids.update(intermediate)
            self.draw_gaze(self.state["x"], self.state["y"], pupil=self.state["pupil"])
            time.sleep(delay)
