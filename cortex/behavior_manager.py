from .behavior_plan import BehaviorPlan

# Map Hal's internal moods to valid LCD expression keys
MOOD_TO_EXPRESSION = {
    "happy": "positive",
    "neutral": "neutral",
    "cautious": "skeptical",
    "curious": "anticipation",
    "sleepy": "sleepy"
}

class BehaviorManager:
    """
    Behavior-driven planner.
    Converts a behavior string into a BehaviorPlan.
    """

    def build_plan(self, decision):
        plan = BehaviorPlan()

        # Extract everything from the fused packet
        behavior = decision.get("behavior")
        speech = decision.get("speech", [])
        nonverbal = decision.get("nonverbal_suggestions", {})
        initiative = decision.get("initiative_intent")
        perception = decision.get("perception")          # REAL perception snapshot
        world_state = decision.get("world_state")        # REAL world state
        internal_state = decision.get("internal_state")  # REAL internal state

        # --- SPEECH ---------------------------------------------------------
        # Normalize speech to always be a list of dicts
        if isinstance(speech, dict):
            speech = [speech]
        plan.speech["output_speech"] = speech

        # --- NONVERBAL ------------------------------------------------------
        plan.nonverbal["gaze"] = nonverbal.get("gaze", [])
        plan.nonverbal["expression"] = nonverbal.get("expression", [])
        plan.nonverbal["sounds"] = nonverbal.get("sounds", [])
        plan.nonverbal["actions"] = nonverbal.get("actions", [])

        # --- MEMORY + WORLD UPDATES ----------------------------------------
        # These now come from system, not the LLM
        plan.memory["write"] = decision.get("memory_updates", [])
        plan.world_state["update"] = decision.get("world_updates", [])

        # --- BEHAVIOR HANDLER ----------------------------------------------
        handler = getattr(self, f"_plan_{behavior}", None)
        if callable(handler):
            handler(plan, perception, internal_state, initiative)
        else:
            self._plan_observe(plan, perception, internal_state, initiative)

        return plan


    # ----------------- behaviors -----------------

    def _plan_converse(self, plan, perception, internal_state, initiative):
        speech = perception.get("speech", [])

        # Add emotion to speech
        for s in speech:
            s["emotion"] = internal_state.mood

        if speech:
            plan.speech["output_speech"] = speech
        else:
            text = internal_state.last_user_text or ""
            if text:
                plan.speech["output_speech"] = [{
                    "text": f"I've been thinking about what you said: {text[:80]}...",
                    "emotion": internal_state.mood
                }]

        # Expression based on Hal's internal mood
        expr = MOOD_TO_EXPRESSION.get(internal_state.mood, "neutral")
        plan.nonverbal["expression"] = [{"mood": expr, "when": "start"}]

        plan.nonverbal["gaze"] = [{"mode": "center", "when": "start"}]


    def _plan_greet(self, plan, perception, internal_state, initiative):
        speech = perception.get("speech", [])

        for s in speech:
            s["emotion"] = internal_state.mood

        if speech:
            plan.speech["output_speech"] = speech
        else:
            name = internal_state.last_speaker or "there"
            plan.speech["output_speech"] = [{
                "text": f"Hello, {name}! It's good to see you.",
                "emotion": internal_state.mood
            }]

        expr = MOOD_TO_EXPRESSION.get(internal_state.mood, "neutral")
        plan.nonverbal["expression"] = [{"mood": expr, "when": "start"}]
        plan.nonverbal["gaze"] = [{"mode": "center", "when": "start"}]


    def _plan_idle_fidget(self, plan, perception, internal_state, initiative):
        plan.actions.append({
            "category": "subtle",
            "type": "fidget_small",
            "when": "start"
        })

        plan.nonverbal["gaze"] = [{"mode": "wander", "when": "start"}]


    def _plan_idle(self, plan, perception, internal_state, initiative):
        pass


    def _plan_observe(self, plan, perception, internal_state, initiative):
        plan.nonverbal["gaze"] = [{"mode": "center", "when": "start"}]


    def _plan_act(self, plan, perception, internal_state, initiative):
        actions = perception.get("actions", [])
        for act in actions:
            if isinstance(act, dict) and "category" in act:
                if "when" not in act:
                    act["when"] = "start"
                plan.actions.append(act)


    def _plan_internal(self, plan, perception, internal_state, initiative):
        pass


    def _plan_explore(self, plan, perception, internal_state, initiative):
        plan.speech["output_speech"] = [{
            "text": "I can't explore right now; it's not safe in this environment.",
            "emotion": internal_state.mood
        }]
        expr = MOOD_TO_EXPRESSION.get(internal_state.mood, "neutral")
        plan.nonverbal["expression"] = [{"mood": expr, "when": "start"}]
        plan.actions.clear()
