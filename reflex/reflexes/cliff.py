from reflex.reflexive_layer import Reflex
from cortex.behavior_plan import BehaviorPlan


class CliffReflex(Reflex):
    priority = 95

    def should_trigger(self, perception, world_state, hardware_state):
        event = perception.get("cliff", {}).get("cliff_detected")
        return event == 1

    def execute(self):
        plan = BehaviorPlan()

        # stop motion
        plan.actions.append({"category": "full-body", "type": "stop"})
        # step back (motors layer will decide what this means later)
        plan.actions.append({"category": "full-body", "type": "step_back"})

        # nonverbal reactions
        plan.nonverbal["expression"].append({"mood": "suspicious"})
        plan.nonverbal["gaze"].append({"mode": "down"})
        plan.nonverbal["sounds"].append({"category": "cliff_detected"})

        return plan