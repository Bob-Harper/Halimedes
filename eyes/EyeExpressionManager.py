from typing import TYPE_CHECKING, Optional
if TYPE_CHECKING:
    from eyes.EyeFrameComposer import EyeFrameComposer
import asyncio
import json
import os
import traceback
with open(os.path.join(os.path.dirname(__file__), "expressions", "eye_expressions.json"), "r") as f:
    expression_map = json.load(f)


class EyeExpressionManager:
    def __init__(self,
                 duration=0.15,
                 eyelid_hold_closed=0.08,
                 multi_file=False
                 ):
        print("[ExprMgr] Constructed at:")
        traceback.print_stack(limit=5)
        self.composer: Optional['EyeFrameComposer'] = None
        self.multi_file = multi_file
        self.expressions = self._load_expressions()
        # ensure all four corners exist
        self.lids = {}
        self.expression_map = self.expressions
        self.duration = duration
        self.eyelid_hold_closed = eyelid_hold_closed
        self.timer = 0.0
        self.active = False
        self.phase = None  # 'closing', 'eyelid_stay_closed', 'opening'
        self.closed_cfg = {
            "eye1_top_left": 82, "eye1_top_right": 82,
            "eye1_bottom_left": 82, "eye1_bottom_right": 82,
            "eye2_top_left": 82, "eye2_top_right": 82,
            "eye2_bottom_left": 82, "eye2_bottom_right": 82,
        }
        print(f"[ExprMgr] id(self): {id(self)} composer: {id(self.composer)}")

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
        self.blink_start_cfg = self.lids.copy()  # capture expression *at start*


    def is_blinking(self):  # CHECK FOR REDUNDANCY REMOVAL
        print(f"[ExprMgr] id(self): {id(self)}")
        print(f"[EyelidController] www Checking if blinking: {self.active}")
        return self.active

    def update_blink(self, dt):
        print(f"[ExprMgr] id(self): {id(self)}")
        if not self.active:
            return None
        
        print(f"[Blink] Phase: {self.phase}, timer: {self.timer:.3f}")
        self.timer += dt

        if self.phase == 'closing':
            if self.timer >= self.duration:
                self.phase = 'opening'
                self.timer = 0.0
            t = self.timer / self.duration
            print(f"[Blink] CLOSING t={t:.2f}")
            # print(f"[Blink] Interpolating FROM {self.blink_start_cfg} TO {self.closed_cfg}")
            return self._interpolate(self.blink_start_cfg, self.closed_cfg, t)

        # elif self.phase == 'eyelid_stay_closed':
        #     if self.timer >= self.eyelid_hold_closed:
        #         self.phase = 'opening'
        #         self.timer = 0.0
        #     print(f"[Blink] STAY CLOSED using: {self.closed_cfg}")
        #     return self.closed_cfg

        elif self.phase == 'opening':
            if self.timer >= self.duration:
                self.active = False
                self.phase = None
                print("[Blink] COMPLETE. Returning to expression lids.")
                return None
            t = self.timer / self.duration
            current_lids = self.get_mask_config()
            print(f"[Blink] OPENING t={t:.2f}")
            # print(f"[Blink] Interpolating FROM {self.closed_cfg} TO {current_lids}")
            return self._interpolate(self.closed_cfg, current_lids, t)


    def _interpolate(self, from_cfg, to_cfg, t):
        missing_keys = [k for k in from_cfg if k not in to_cfg]
        if missing_keys:
            print(f"[EyelidController] !!! ERROR: Missing keys in target config: {missing_keys}")
            raise KeyError(missing_keys[0])

        return {
            k: int(round((1 - t) * from_cfg[k] + t * to_cfg[k]))
            for k in from_cfg
        }

    def set_eyelid_expression(self, name: str):
        # Only skip if lids already populated
        if self.state.expression == name and self.lids:
            print(f"[ExprMgr] === Skipping redundant eyelid config for '{name}'")
            return
        self.state.expression = name  # make sure this tracks the last set
        exp = self.expression_map.get(name)
        
        print("[ExprMgr] rrr Switching to expression:", name)
        print("[ExprMgr] fff Loaded mask:", exp)        
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
        print(f"[EyelidController] vvv Current eyelid config: {self.lids}") 

    def get_mask_config(self):
        if self.lids:
            return self.lids.copy()

        print(f"[EyelidController] Lids not set — attempting to recover from current expression '{self.state.expression}'")

        fallback_expr = self.expression_map.get(self.state.expression)
        if fallback_expr:
            print(f"[EyelidController] Recovered lids from current expression '{self.state.expression}'")
            return fallback_expr.copy()

        neutral = self.expression_map.get("neutral")
        if neutral:
            print("[EyelidController] Using hard fallback: 'neutral'")
            return neutral.copy()

        raise RuntimeError(" ExpressionManager: No eyelid mask available. Expression state is invalid or missing in config.")

    def _load_expressions(self):
        print(f"[ExprMgr] id(self): {id(self)}")
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
        if self.active:  # blinking in progress
            print("[ExprMgr] update_expression skipped — currently blinking")
            return
        print(f"[ExprMgr] id(self): {id(self)}")
        print(f"[ExprMgr] rdx update_expression: using '{self.state.expression}' vs last set '{self._last_expression_set}'")
        print(f"[ExprMgr] update_expression: current={self.state.expression}, last={self._last_expression_set}")

        assert self.composer is not None, "Composer must be set before updating expression"
        current_expr = self.state.expression  # use internal state, not composer's
        print(f"[ExprMgr] tfc update_expression: using '{self.state.expression}' vs last set '{self._last_expression_set}'")

        self.set_eyelid_expression(current_expr)
        self.composer.set_eyelids(self.get_mask_config())
        # print(f"[EyeExpressionManager] ggg [FORCED] Applied expression '{current_expr}' with lids: {self.get_mask_config()}")

    def get_current_mask(self):  # CHECK FOR REDUNDANCY REMOVAL
        print(f"[ExprMgr] id(self): {id(self)}")
        # Return the current eyelid mask configuration
        # print("[EyeExpressionManager] yyy Getting current mask configuration")
        return self.get_mask_config()

    async def animate_expression(self, mood: str, steps=16, delay=0.01):
        print(f"[ExprMgr] id(self): {id(self)}")
        assert self.composer is not None, "Composer must be set before animating expression"
        target = self.expression_map.get(mood)
        print(f"[EyeExpressionManager] hhh Animating expression: {mood} with target config: {target}")
        if not target:
            print(f"[EyeExpressionManager] Unknown expression: {mood}")
            return

        start_cfg = self.lids.copy()
        for step in range(1, steps + 1):
            frac = step / steps
            # print(f"[EyeExpressionManager] nnn Tweening step {step}/{steps} with fraction {frac}")
            interp_cfg = {
                k: int(start_cfg.get(k, 0) + (target.get(k, 0) - start_cfg.get(k, 0)) * frac)
                for k in target
            }
            self.lids.update(interp_cfg)
            self.current_expression = mood

            # Hand off the current state to Composer
            self.composer.set_eyelids(interp_cfg)
            print(f"[EyeExpressionManager] uuu Updated eyelids to {interp_cfg}")
            await asyncio.sleep(delay)

        self.composer.set_eyelids(None)  # release override once tween done
        # print("[EyeExpressionManager] jjj Animation complete, eyelids cleared")

    async def set_expression(self, mood: str):
        print(f"[ExprMgr] !!! NEW EXPRESSION SET: {mood}")
        
        # only skip if lids are already set to this mood
        if self.state.expression == mood and self.lids:
            print(f"[ExprMgr] (SKIP) Already in expression '{mood}'")
            return

        assert self.composer is not None, "Composer must be set before animating expression"

        self.state.expression = mood
        self._last_expression_set = mood
        print(f"[ExprMgr]     current: {self.state.expression}   last set: {self._last_expression_set}")
        print(f"[ExprMgr]     lids?: {'yes' if self.lids else 'no'}")

        self.set_eyelid_expression(mood)
        print(f"[ExprMgr] >>> set lids to: {self.lids}")
        self.composer.set_eyelids(self.get_mask_config())
