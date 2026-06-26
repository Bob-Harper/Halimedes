# kernel/reflexes/battery_critical.py

from kernel.reflexive_layer import Reflex

class BatteryCriticalReflex(Reflex):
    priority = 100

    def should_trigger(self, perception, world_state, internal_state, hardware_state):
        status = hardware_state.status.get("battery", {}).get("status")
        return status == "Critical"

    def execute(self):
        return {"intent": "emergency_return_to_charger"}
