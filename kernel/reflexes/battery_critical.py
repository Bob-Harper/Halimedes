# kernel/reflexes/battery_critical.py

from kernel.reflexive_layer import Reflex

class BatteryCriticalReflex(Reflex):
    priority = 100

    def should_trigger(self, perception, world_state, internal_state):
        return internal_state.battery_level < 5

    def execute(self):
        return {"intent": "emergency_return_to_charger"}
