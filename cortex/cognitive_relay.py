# cortex/cognition_loop.py

class CognitiveRelay:
    """
    The brainstem: runs each cognition tick.
    Pulls perception → builds context → decides → executes.
    """

    def __init__(
        self,
        perception_manager,
        context_builder,
        initiative_manager,
        decision_manager,
        behavior_manager,
        behavior_executor,
        internal_state_manager,   # ← ADD THIS
    ):
        self.perception = perception_manager
        self.context = context_builder
        self.initiative = initiative_manager
        self.decision = decision_manager
        self.behavior_manager = behavior_manager
        self.executor = behavior_executor
        self.internal_state = internal_state_manager   # ← STORE IT


    async def tick(self, server_json):

        # Snapshot perception + context
        raw = self.perception.snapshot()
        ctx = self.context.build(raw)

        # Initiative tick
        if hasattr(self.initiative, "tick"):
            self.initiative.tick()

        initiative_intent = self.initiative.suggest(
            self.perception.snapshot(),
            world_state=self.context.world_state,
            internal_state=self.internal_state
        )

        # LLM behavior + expressive suggestions
        llm_behavior = server_json.get("behavior")
        llm_speech = server_json.get("speech", [])
        llm_nonverbal = server_json.get("nonverbal_suggestions", {})

        # Fuse into a single decision packet
        decision = {
            "behavior": llm_behavior,
            "speech": llm_speech,
            "nonverbal_suggestions": llm_nonverbal,
            "initiative_intent": initiative_intent,
            "perception": raw,
            "world_state": self.context.world_state,
            "internal_state": self.internal_state,  # or snapshot()
            # later: "memory_updates": ..., "world_updates": ... (from YOUR code, not LLM)
        }

        plan = self.behavior_manager.build_plan(decision)
        print(f"\n[Cognition] Plan as sent to executor.run_plan: \n{plan}\n\n")

        await self.executor.run_plan(plan)
        self.perception.reset()


    def _merge_intents(self, initiative):

        if initiative:
            return {"intent": initiative}

        return {"intent": "none"}