from eyes.EyeFrameComposer import EyeFrameComposer, EyeState, expression_map
from typing import Optional
import asyncio
import json
import os


class EyeExpressionManager:
    def __init__(self,
                 composer: Optional['EyeFrameComposer'] = None,
                 duration=0.15,
                 hold=0.08,
                 multi_file=False
                 ):
        self.composer = composer
        self.multi_file = multi_file
        self.expressions = self._load_expressions()
        self.state = EyeState()
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
        self.duration = duration
        self.hold = hold
        self.timer = 0.0
        self.active = False
        self.phase = None  # 'closing', 'holding', 'opening'

        self.closed_cfg = {
            "eye1_top_left": 0, "eye1_top_right": 0,
            "eye1_bottom_left": 0, "eye1_bottom_right": 0,
            "eye2_top_left": 0, "eye2_top_right": 0,
            "eye2_bottom_left": 0, "eye2_bottom_right": 0,
        }

    def trigger(self):
        self.timer = 0.0
        self.active = True
        self.phase = 'closing'

    def is_blinking(self):
        return self.active

    def update_blink(self, dt):
        if not self.active:
            return None

        self.timer += dt

        if self.phase == 'closing':
            if self.timer >= self.duration:
                self.phase = 'holding'
                self.timer = 0.0
            t = self.timer / self.duration
            return self._interpolate(self.get_current_mask(), self.closed_cfg, t)

        elif self.phase == 'holding':
            if self.timer >= self.hold:
                self.phase = 'opening'
                self.timer = 0.0
            return self.closed_cfg

        elif self.phase == 'opening':
            if self.timer >= self.duration:
                self.active = False
                self.phase = None
                return None
            t = self.timer / self.duration
            return self._interpolate(self.closed_cfg, self.get_current_mask(), t)

    def _interpolate(self, from_cfg, to_cfg, t):
        return {
            k: int(round((1 - t) * from_cfg[k] + t * to_cfg[k]))
            for k in from_cfg
        }

    def set_eyelid_expression(self, name: str):
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
        print(f"[get_current_mask] Current mask: {lids}")
        return lids

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
            except Exception as e:
                print(f"[ExpressionManager] Failed to load expressions: {e}")
        return expressions

    def update_expression(self):
        assert self.composer is not None, "Composer must be set before updating expression"
        if self.composer.state.expression:
            self.set_eyelid_expression(self.composer.state.expression)
            self.composer.set_eyelids(self.get_mask_config())
        else:
            self.composer.set_eyelids(None)

    def get_current_mask(self):
        # Return the current eyelid mask configuration
        return self.get_mask_config()

    async def animate_expression(self, mood: str, steps=16, delay=0.01):
        assert self.composer is not None, "Composer must be set before animating expression"
        target = self.expression_map.get(mood)
        if not target:
            print(f"[EyeExpressionManager] Unknown expression: {mood}")
            return

        start_cfg = self.lids.copy()
        for step in range(1, steps + 1):
            frac = step / steps
            interp_cfg = {
                k: int(start_cfg.get(k, 0) + (target.get(k, 0) - start_cfg.get(k, 0)) * frac)
                for k in target
            }
            self.lids.update(interp_cfg)
            self.current_expression = mood

            # Hand off the current state to Composer
            self.composer.set_eyelids(interp_cfg)
            await asyncio.sleep(delay)

        self.composer.set_eyelids(None)  # release override once tween done

    # set_expression changes the high-level mood, the expression manager handles the lid config
    async def set_expression(self, mood: str):
        self.state.expression = mood
        self._dirty = True