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
        behavior_executor,
        internal_state_manager,   # ← ADD THIS
    ):
        self.perception = perception_manager
        self.context = context_builder
        self.initiative = initiative_manager
        self.decision = decision_manager
        self.executor = behavior_executor
        self.internal_state = internal_state_manager   # ← STORE IT


    async def tick(self, server_intent):
        # 1. Snapshot perception
        raw = self.perception.snapshot()

        # 2. Build context (this updates world_state + internal_state)
        ctx = self.context.build(raw)

        # 3. Tick initiative timers
        if hasattr(self.initiative, "tick"):
            self.initiative.tick()

        # 4. Compute initiative suggestion
        initiative_intent = self.initiative.suggest(
            perception=self.perception,
            world_state=self.context.world_state,
            internal_state=self.internal_state
        )

        # 5. Merge initiative + server intent
        final_intent = self._merge_intents(initiative_intent, server_intent)

        # 6. Decision layer
        plan = self.decision.decide(
            perception={**raw, **ctx},
            server_intent=final_intent
        )

        # 7. Execute behavior
        await self.executor.run_plan(plan)

        # 8. Reset perception
        self.perception.reset()

    def _merge_intents(self, initiative, server):
        # Server intent wins if user spoke or server has a real command
        if server and server.get("intent") not in (None, "none"):
            return server

        # Initiative intent wins if server is silent
        if initiative:
            return {"intent": initiative}

        return {"intent": "none"}