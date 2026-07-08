# reflex/reflexive_layer.py
from typing import List


class Reflex:
    priority = 0  # higher = more urgent

    def should_trigger(self, sensor_state, world_state, hardware_state):
        # print("ShouldTrigger: fired")
        raise NotImplementedError

    def return_plan(self, sensor_state, world_state, hardware_state):
        # print("ReturnPlan: fired")
        raise NotImplementedError


class ReflexEngine:
    def __init__(self, reflexes: List[Reflex]):
        self.reflexes = sorted(reflexes, key=lambda r: r.priority, reverse=True)
        # print("[Startup] Loaded reflexes:", [r.__class__.__name__ for r in self.reflexes])

    async def check_and_plan(self, sensor_state, world_state, hardware_state, executor):
        # print("Loaded reflexes:", [r.__class__.__name__ for r in self.reflexes])
        for reflex in self.reflexes:
                if reflex.should_trigger(sensor_state, world_state, hardware_state):

                    plan = reflex.return_plan(
                        sensor_state,
                        world_state,
                        hardware_state
                    )

                    # print(f"Reflex plan created: {reflex.__class__.__name__} with plan: {plan}")
                    return plan
        # print("No reflex triggered.")
        return False
