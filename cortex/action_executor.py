# cortex/action_executor.py
import asyncio


class ActionExecutor:
    """
    Executes a BehaviorPlan produced by the DecisionManager.
    This is the ONLY layer that touches hardware.
    """

    def __init__(self, motors=None, searchlight=None, audio=None, gaze_channel=None, expression_channel=None):
        self.motors = motors
        self.searchlight = searchlight
        self.audio = audio
        self.gaze = gaze_channel
        self.expression = expression_channel
        self._movement_lock = asyncio.Lock()
        self._current_movement_task = None

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
                await self.audio.speak(text, emotion)

    # ------------------------------------------------------------------
    # GAZE
    # ------------------------------------------------------------------
    def _execute_gaze(self, gaze_list):
        if not self.gaze:
            return

        for g in gaze_list:
            mode = g.get("mode")

            if mode == "center":
                asyncio.create_task(self.gaze.move_to(90, 90, 1.0))
            elif mode == "left":
                asyncio.create_task(self.gaze.move_to(80, 90, 1.0))
            elif mode == "right":
                asyncio.create_task(self.gaze.move_to(100, 90, 1.0))
            elif mode == "up":
                asyncio.create_task(self.gaze.move_to(90, 80, 1.0))
            elif mode == "down":
                asyncio.create_task(self.gaze.move_to(90, 100, 1.0))
            elif mode == "wander":
                asyncio.create_task(self.gaze.wander())
            else:
                print(f"[Gaze] Unknown mode: {mode}")

    # ------------------------------------------------------------------
    # EXPRESSIONS
    # ------------------------------------------------------------------
    def _execute_expression(self, expr_list):
        if not self.expression:
            return
        for e in expr_list:
            mood = e.get("mood")
            if mood:
                asyncio.create_task(self.expression.set_mood(mood))

    # ------------------------------------------------------------------
    # ACTIONS (movement, searchlight, etc.)
    # ------------------------------------------------------------------
    async def _run_movement(self, func, *args, **kwargs):
        # Cancel any ongoing movement
        if self._current_movement_task and not self._current_movement_task.done():
            self._current_movement_task.cancel()
            try:
                await self._current_movement_task
            except asyncio.CancelledError:
                pass

        # Start new movement
        self._current_movement_task = asyncio.create_task(
            self._movement_serialized(func, *args, **kwargs)
        )

    async def _movement_serialized(self, func, *args, **kwargs):
        async with self._movement_lock:
            await asyncio.to_thread(func, *args, **kwargs)

    def _execute_actions(self, actions_list):
        for act in actions_list:
            category = act.get("category")

            # Searchlight control
            if category == "searchlight" and self.searchlight:
                level = act.get("level", 0)
                if hasattr(self.searchlight, "speed"):
                    self.searchlight.speed(level)

            # Subtle idle movement
            elif category == "subtle" and self.motors:
                if hasattr(self.motors, "do_idle_fidget"):
                    asyncio.create_task(self._run_movement(self.motors.do_idle_fidget))

            # Expressive gesture
            elif category == "expressive" and self.motors:
                if hasattr(self.motors, "do_expressive_motion"):
                    asyncio.create_task(self._run_movement(self.motors.do_expressive_motion))

            # Full-body movement
            elif category == "full-body" and self.motors:
                if hasattr(self.motors, "do_full_body_motion"):
                    asyncio.create_task(self._run_movement(self.motors.do_full_body_motion))

    # ------------------------------------------------------------------
    # SOUNDS (non-speech)
    # ------------------------------------------------------------------
    def _execute_sounds(self, sounds_list):
        if not self.audio:
            return

        for snd in sounds_list:
            category = snd.get("category")
            if category:
                self.audio.emotion_handler.play_sound(category)

