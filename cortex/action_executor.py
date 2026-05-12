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
    async def execute(self, plan):
        """
        Execute speech, nonverbal actions, and world/memory updates.
        NOTE: BehaviorExecutor will call the channel methods directly,
        but this remains for compatibility if needed.
        """
        if not plan:
            return

        # Speech
        if plan.speech:
            await self._execute_speech(plan.speech)

        # Nonverbal
        nonverbal = plan.nonverbal or {}
        self._execute_gaze(nonverbal.get("gaze", []))
        self._execute_expression(nonverbal.get("expression", []))
        self._execute_actions(nonverbal.get("actions", []))
        self._execute_sounds(nonverbal.get("sounds", []))

    # ------------------------------------------------------------------
    # SPEECH
    # ------------------------------------------------------------------
    async def _execute_speech(self, speech_list):
        if not self.audio:
            return

        for entry in speech_list:
            text = entry.get("text")
            emotion = entry.get("emotion", "neutral")
            if text:
                await self.audio.speak_with_flite(text, emotion)
                
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
                # If your eye animator supports wandering:
                if hasattr(self.eyes, "look_wander"):
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

            # Subtle idle movement
            if category == "subtle" and self.motors:
                if hasattr(self.motors, "do_idle_fidget"):
                    self.motors.do_idle_fidget()

            # Expressive gesture
            elif category == "expressive" and self.motors:
                if hasattr(self.motors, "do_expressive_motion"):
                    self.motors.do_expressive_motion()

            # Full-body movement
            elif category == "full-body" and self.motors:
                if hasattr(self.motors, "do_full_body_motion"):
                    self.motors.do_full_body_motion()

            # Searchlight control
            elif category == "searchlight" and self.searchlight:
                level = act.get("level", 0)
                if hasattr(self.searchlight, "speed"):
                    self.searchlight.speed(level)

    # ------------------------------------------------------------------
    # SOUNDS (non-speech)
    # ------------------------------------------------------------------
    def _execute_sounds(self, sounds_list):
        if not self.audio:
            return

        for snd in sounds_list:
            category = snd.get("category")
            if category and hasattr(self.audio, "play_effect"):
                self.audio.play_effect(category)
