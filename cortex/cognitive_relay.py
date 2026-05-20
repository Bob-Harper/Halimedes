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

        # Snapshot perception
        raw = self.perception.snapshot()

        # Build context
        ctx = self.context.build(raw)

        # Initiative tick
        if hasattr(self.initiative, "tick"):
            self.initiative.tick()

        # Initiative suggestion  ** WHY IS IT NOT USED.  WE WILL ATTEND TO THAT.
        initiative_intent = self.initiative.suggest(
            self.perception.snapshot(),
            world_state=self.context.world_state,
            internal_state=self.internal_state
        )

        # Behavior from server
        behavior = server_json["behavior"]

        # Build plan using server output
        plan = self.behavior_manager.build_plan(
            behavior=behavior,
            perception=server_json,
            internal_state=self.internal_state
        )
        print(f"\n[Cognition] Plan as sent to executor.run_plan: \n{plan}\n\n")
        # Execute
        await self.executor.run_plan(plan)

        # Reset perception
        self.perception.reset()



    def _merge_intents(self, initiative):

        if initiative:
            return {"intent": initiative}

        return {"intent": "none"}