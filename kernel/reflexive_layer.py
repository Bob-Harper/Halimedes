# kernel/reflexive_layer.py
from typing import List


class Reflex:
    priority = 0  # higher = more urgent

    def should_trigger(self, perception, world_state, internal_state, hardware_state):
        raise NotImplementedError

    def execute(self):
        raise NotImplementedError


class ReflexEngine:
    def __init__(self, reflexes: List[Reflex]):
        self.reflexes = sorted(reflexes, key=lambda r: r.priority, reverse=True)

    async def check_and_execute(self, perception, world_state, internal_state, hardware_state, executor):
        for reflex in self.reflexes:
            if reflex.should_trigger(perception, world_state, internal_state, hardware_state):
                plan = reflex.execute()
                await executor.run_plan(plan)
                return plan
        return False
