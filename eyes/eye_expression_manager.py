import json
import os
from eyes.core.eyelid_controller import EyelidController

class EyeExpressionManager:
    def __init__(self, animator, multi_file=False):
        self.animator = animator
        self.multi_file = multi_file
        self.lid_control = EyelidController() 
        self.expressions = self._load_expressions()

    def _load_expressions(self):
        expressions = {}
        base_dir = os.path.dirname(__file__)
        expr_path = os.path.join(base_dir, "expressions/eye_expressions.json")

        if self.multi_file:
            for file in os.listdir(base_dir):
                if file.endswith(".json") and file != "expressions/eye_expressions.json":
                    path = os.path.join(base_dir, file)
                    try:
                        with open(path, "r") as f:
                            name = os.path.splitext(file)[0]
                            expressions[name] = json.load(f)
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

    def set_expression(self, name: str):
        self.lid_control.set_expression(name) 

    def draw_expression(self, expression):
        config = self.expressions.get(expression)
        if not config:
            print(f"[ExpressionManager] Unknown expression: '{expression}'")
            return

        try:
            # Apply eyelid positions
            for lid_key in [
                'eye1_top_left', 'eye1_top_right', 
                'eye1_bottom_left', 'eye1_bottom_right', 
                'eye2_top_left', 'eye2_top_right', 
                'eye2_bottom_left', 'eye2_bottom_right']:
                if lid_key in config:
                    self.animator.set_expression(lid_key, config[lid_key])

        except Exception as e:
            print(f"[ExpressionManager] Error applying '{expression}': {e}")
