from typing import TYPE_CHECKING, Optional
if TYPE_CHECKING:
    from eyes.EyeFrameComposer import EyeFrameComposer
import asyncio
import json
import os

with open(os.path.join(os.path.dirname(__file__), "expressions", "eye_expressions.json"), "r") as f:
    expression_map = json.load(f)


class EyeExpressionManager:
    def __init__(self,
                 duration=0.15,
                 eyelid_hold_closed=0.08,
                 multi_file=False
                 ):
        self.composer: Optional['EyeFrameComposer'] = None
        self.multi_file = multi_file
        self.expressions = self._load_expressions()
        self.lids = {}
        self.expression_map = self.expressions
        self.duration = duration
        self.eyelid_hold_closed = eyelid_hold_closed
        self.timer = 0.0
        self.active = False
        self.phase = None
        self.closed_cfg = {
            "eye1_top_left": 82, "eye1_top_right": 82,
            "eye1_bottom_left": 82, "eye1_bottom_right": 82,
            "eye2_top_left": 82, "eye2_top_right": 82,
            "eye2_bottom_left": 82, "eye2_bottom_right": 82,
        }
        self.animating_expression = False

    def setup(self, composer):
        self.composer = composer

    @property
    def state(self):
        assert self.composer is not None, "Composer is not set"
        return self.composer.state

    def trigger(self):
        self.timer = 0.0
        self.active = True
        self.phase = 'closing'
        self.blink_start_cfg = self.lids.copy()
        self.blink_target_cfg = self.get_mask_config().copy()  # <- 💡 capture target now

    def is_blinking(self):
        return self.active

    def update_blink(self, dt):
        if not self.active:
            return None

        self.timer += dt

        if self.phase == 'closing':
            if self.timer >= self.duration:
                self.phase = 'eyelid_stay_closed'
                self.timer = 0.0
                return self.closed_cfg  # <---- RETURN CLOSED DIRECTLY on transition

            t = self.timer / self.duration
            return self._interpolate(self.blink_start_cfg, self.closed_cfg, t)
        
        elif self.phase == 'eyelid_stay_closed':
            if self.timer >= self.eyelid_hold_closed:
                self.phase = 'opening'
                self.timer = 0.0
            return self.closed_cfg

        elif self.phase == 'opening':
            if self.timer >= self.duration:
                self.active = False
                self.phase = None
                return None
            t = self.timer / self.duration
            current_lids = self.get_mask_config()
            return self._interpolate(self.closed_cfg, current_lids, t)

    def _interpolate(self, from_cfg, to_cfg, t):
        missing_keys = [k for k in from_cfg if k not in to_cfg]
        if missing_keys:
            raise KeyError(missing_keys[0])

        interpolated = {
            k: int(round((1 - t) * from_cfg[k] + t * to_cfg[k]))
            for k in from_cfg
        }
        return interpolated

    def set_eyelid_expression(self, name: str):
        if self.state.expression == name:
            exp = self.expression_map.get(name)
            if exp and self.lids == exp:
                return
            else:
                print(f"[ExprMgr] --- Expression '{name}' already set, but lids do not match — forcing update")

        self.state.expression = name
        exp = self.expression_map.get(name)

        if not exp:
            print(f"[EyelidController] Unknown expression: {name}")
            return

        for corner in (
            "eye1_top_left", "eye1_top_right",
            "eye1_bottom_left", "eye1_bottom_right",
            "eye2_top_left", "eye2_top_right",
            "eye2_bottom_left", "eye2_bottom_right"
        ):
            if corner in exp:
                self.lids[corner] = exp[corner]

    def get_mask_config(self):
        if self.lids:
            return self.lids.copy()

        fallback_expr = self.expression_map.get(self.state.expression)
        if fallback_expr:
            return fallback_expr.copy()

        neutral = self.expression_map.get("neutral")
        if neutral:
            return neutral.copy()

        raise RuntimeError("ExpressionManager: No eyelid mask available. Expression state is invalid or missing in config.")

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
        if self.active or self.animating_expression:  # blinking or animating
            return
        
        assert self.composer is not None, "Composer must be set before updating expression"
        current_expr = self.state.expression

        self.set_eyelid_expression(current_expr)
        mask = self.get_mask_config()
        self.composer.set_eyelids(mask)

    def get_current_mask(self):
        return self.get_mask_config()

    async def animate_expression(self, mood: str, steps=16, delay=0.01):
        assert self.composer is not None, "Composer must be set before animating expression"

        target = self.expression_map.get(mood)
        if not target:
            print(f"[ExprMgr] Unknown expression: {mood}")
            return

        self.animating_expression = True
        start_cfg = self.lids.copy()

        for step in range(1, steps + 1):
            frac = step / steps
            interp_cfg = {
                k: int(start_cfg.get(k, 0) + (target.get(k, 0) - start_cfg.get(k, 0)) * frac)
                for k in target
            }
            self.composer.set_eyelids(interp_cfg)
            await asyncio.sleep(delay)

        # Finalize the new expression
        self.state.expression = mood
        self.set_eyelid_expression(mood)
        self.composer.set_eyelids(None)
        self.animating_expression = False
