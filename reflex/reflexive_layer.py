# reflex/reflexive_layer.py
from typing import List


class Reflex:
    priority = 0  # higher = more urgent

    def should_trigger(self, sensor_state, world_state, hardware_state):
        raise NotImplementedError

    def return_plan(self, sensor_state, world_state, hardware_state):
        raise NotImplementedError


class ReflexEngine:
    def __init__(self, reflexes: List[Reflex]):
        self.reflexes = sorted(reflexes, key=lambda r: r.priority, reverse=True)

    async def check_and_plan(self, sensor_state, world_state, hardware_state, executor):
        for reflex in self.reflexes:
                if reflex.should_trigger(sensor_state, world_state, hardware_state):

                    plan = reflex.return_plan(
                        sensor_state,
                        world_state,
                        hardware_state
                    )

                    return plan
        return False
