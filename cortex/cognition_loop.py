# cortex/cognition_loop.py

import time
from cortex.perception_snapshot import PerceptionSnapshot

class CognitionLoop:
    """
    The brainstem: runs each cognition tick.
    Pulls perception → builds context → wraps snapshot → decides → executes.
    """

    def __init__(
        self,
        perception_manager,
        context_builder,
        initiative_manager,
        decision_manager,
        action_executor,
        tick_rate=0.1,
    ):
        self.perception = perception_manager
        self.context = context_builder
        self.initiative = initiative_manager
        self.decision = decision_manager
        self.executor = action_executor
        self.tick_rate = tick_rate

    # ------------------------------------------------------------------
    # SINGLE TICK
    # ------------------------------------------------------------------
    def tick(self, server_intent=None):
        server_intent = server_intent or {}

        # 1. Raw perception snapshot
        raw = self.perception.snapshot()

        # 2. Derived context
        ctx = self.context.build(raw)

        # 3. Initiative suggestion (optional)
        initiative = self.initiative.suggest(
            ctx,
            self.decision.internal_state
        )
        if initiative:
            # Inject initiative into server intent
            server_intent = dict(server_intent)
            server_intent["initiative"] = initiative

        # 4. Merge raw + context into unified dict
        merged = {**raw, **ctx}

        # 5. Wrap in PerceptionSnapshot dataclass
        snap = PerceptionSnapshot(**merged)

        # 6. Decision manager → BehaviorPlan
        plan = self.decision.decide(
            perception=snap.__dict__,   # DecisionManager expects a dict
            server_intent=server_intent
        )

        # 7. Execute the plan
        self.executor.execute(plan)

        # 8. Reset transient perception fields
        self.perception.reset()

    # ------------------------------------------------------------------
    # CONTINUOUS LOOP
    # ------------------------------------------------------------------
    def run_forever(self):
        while True:
            self.tick()
            time.sleep(self.tick_rate)
