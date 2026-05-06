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
        action_executor,
    ):
        self.perception = perception_manager
        self.context = context_builder
        self.initiative = initiative_manager
        self.decision = decision_manager
        self.executor = action_executor

    def tick(self, server_intent):
        raw = self.perception.snapshot()
        ctx = self.context.build(raw)
        initiative = self.initiative.suggest(ctx, self.decision.internal_state)
        plan = self.decision.decide(perception={**raw, **ctx}, server_intent=server_intent)
        self.executor.execute(plan)
        self.perception.reset()
