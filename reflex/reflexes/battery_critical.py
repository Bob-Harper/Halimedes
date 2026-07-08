# reflex/reflexes/battery_critical.py

from reflex.reflexive_layer import Reflex

class BatteryCriticalReflex(Reflex):
    priority = 100

    def should_trigger(self, sensor_state, world_state, hardware_state):
        status = hardware_state.status.get("battery", {}).get("status")
        return status == "Critical"

    def return_plan(self, sensor_state, world_state, hardware_state):
        return {"intent": "emergency_return_to_charger"}
