# cortex/behavior_executor.py

import asyncio

class BehaviorExecutor:
    """
    Interprets a BehaviorPlan and schedules its channels.
    This is the layer BETWEEN BehaviorManager and ActionExecutor.
    """

    def __init__(self, action_executor):
        self.action_executor = action_executor
        self.current_task = None
        self.interrupt_flag = False

    # --------------------------------------------------------------
    # PUBLIC API
    # --------------------------------------------------------------
    async def run_plan(self, plan):
        """
        Execute a BehaviorPlan with proper timing, concurrency,
        and interruptibility.
        """
        # Cancel any running behavior if needed
        if self.current_task and plan.should_interrupt:
            self.interrupt_flag = True
            self.current_task.cancel()
            await asyncio.sleep(0)  # yield to cancel

        # Start new behavior
        self.interrupt_flag = False
        self.current_task = asyncio.create_task(self._execute(plan))
        return self.current_task

    # --------------------------------------------------------------
    # INTERNAL EXECUTION
    # --------------------------------------------------------------
    async def _execute(self, plan):
        """
        Break the plan into phases:
        - start
        - during
        - after_speech
        """

        # 1. START PHASE (nonverbal only)
        await self._run_phase(plan, phase="start")

        # 2. SPEECH PHASE (speech + during nonverbal)
        await self._run_speech_with_nonverbal(plan)

        # 3. AFTER-SPEECH PHASE
        await self._run_phase(plan, phase="after_speech")

    # --------------------------------------------------------------
    async def _run_phase(self, plan, phase):
        """
        Run nonverbal actions tagged with a specific phase.
        """
        if self.interrupt_flag:
            return

        nonverbal = plan.nonverbal or {}

        # Gaze
        for g in nonverbal.get("gaze", []):
            if g.get("when") == phase:
                self.action_executor._execute_gaze([g])

        # Expression
        for e in nonverbal.get("expression", []):
            if e.get("when") == phase:
                self.action_executor._execute_expression([e])

        # Actions
        for a in nonverbal.get("actions", []):
            if a.get("when") == phase:
                self.action_executor._execute_actions([a])

        # Sounds
        for s in nonverbal.get("sounds", []):
            if s.get("when") == phase:
                self.action_executor._execute_sounds([s])

    # --------------------------------------------------------------
    async def _run_speech_with_nonverbal(self, plan):
        """
        Speech runs concurrently with 'during' nonverbal actions.
        """
        if self.interrupt_flag:
            return

        speech_list = plan.speech or []
        nonverbal = plan.nonverbal or {}

        # Launch speech
        speech_task = asyncio.create_task(self._speak_all(speech_list))

        # Launch DURING nonverbal
        during_task = asyncio.create_task(
            self._run_phase(plan, phase="during")
        )

        # Wait for speech to finish
        await speech_task

        # Cancel DURING if still running
        if not during_task.done():
            during_task.cancel()

    # --------------------------------------------------------------
    async def _speak_all(self, speech_list):
        """
        Speak each entry in order.
        """
        for entry in speech_list:
            if self.interrupt_flag:
                return
            text = entry.get("text")
            if text:
                await self.action_executor.audio.say(text)
