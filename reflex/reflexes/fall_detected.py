from reflex.reflexive_layer import Reflex
from cortex.behavior_plan import BehaviorPlan


class FallDetectedReflex(Reflex):
    priority = 90

    def should_trigger(self, sensor_state, world_state, hardware_state):
        # STUFF NO IDEA NOTHING WORKS THIS IS BULLSHIT

        return False


    def return_plan(self, sensor_state, world_state, hardware_state):
        us = sensor_state["sensor_status"]["ultrasonic"]

        plan = BehaviorPlan()

        plan.actions.append({"category": "full-body", "type": "stop"})
        plan.actions.append({"category": "expressive", "type": "recover"})

        plan.nonverbal["expression"].append({"mood": "surprised"})
        plan.nonverbal["sounds"].append({"category": "fall"})

        return plan