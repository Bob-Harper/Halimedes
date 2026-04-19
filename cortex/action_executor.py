# cortex/action_executor.py

class ActionExecutor:
    """
    Executes a BehaviorPlan produced by the DecisionManager.
    This is the ONLY layer that touches hardware.
    """

    def __init__(self, motors=None, eyes=None, searchlight=None, audio=None):
        self.motors = motors
        self.eyes = eyes
        self.searchlight = searchlight
        self.audio = audio

    # ------------------------------------------------------------------
    # PUBLIC ENTRYPOINT
    # ------------------------------------------------------------------
    def execute(self, plan):
        """
        Execute speech, nonverbal actions, and world/memory updates.
        """
        if not plan:
            return

        # 1. Speech
        if plan.speech:
            self._execute_speech(plan.speech)

        # 2. Nonverbal (gaze, expressions, actions, sounds)
        nonverbal = plan.nonverbal or {}
        self._execute_gaze(nonverbal.get("gaze", []))
        self._execute_expression(nonverbal.get("expression", []))
        self._execute_actions(nonverbal.get("actions", []))
        self._execute_sounds(nonverbal.get("sounds", []))

        # Memory/world updates are handled by higher layers later
        # (DecisionManager already stores them)

    # ------------------------------------------------------------------
    # SPEECH
    # ------------------------------------------------------------------
    def _execute_speech(self, speech_list):
        if not self.audio:
            return
        for entry in speech_list:
            text = entry.get("text")
            if text:
                self.audio.say(text)

    # ------------------------------------------------------------------
    # GAZE
    # ------------------------------------------------------------------
    def _execute_gaze(self, gaze_list):
        if not self.eyes:
            return
        for g in gaze_list:
            mode = g.get("mode")
            if mode == "center":
                self.eyes.look_center()
            elif mode == "wander":
                self.eyes.look_wander()

    # ------------------------------------------------------------------
    # EXPRESSIONS
    # ------------------------------------------------------------------
    def _execute_expression(self, expr_list):
        if not self.eyes:
            return
        for expr in expr_list:
            mood = expr.get("mood")
            if mood:
                self.eyes.set_mood(mood)

    # ------------------------------------------------------------------
    # ACTIONS (movement, searchlight, etc.)
    # ------------------------------------------------------------------
    def _execute_actions(self, actions_list):
        for act in actions_list:
            category = act.get("category")

            # Full-body movement (placeholder)
            if category == "full-body" and self.motors:
                self.motors.do_full_body_motion()

            # Subtle idle movement
            elif category == "subtle" and self.motors:
                self.motors.do_idle_fidget()

            # Expressive gesture
            elif category == "expressive" and self.motors:
                self.motors.do_expressive_motion()

            # Searchlight control (example)
            if category == "searchlight" and self.searchlight:
                level = act.get("level", 0)
                self.searchlight.speed(level)

    # ------------------------------------------------------------------
    # SOUNDS (non-speech)
    # ------------------------------------------------------------------
    def _execute_sounds(self, sounds_list):
        if not self.audio:
            return
        for snd in sounds_list:
            category = snd.get("category")
            if category:
                self.audio.play_effect(category)
