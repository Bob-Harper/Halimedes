from reflex.reflexive_layer import Reflex


class CliffReflex(Reflex):
    priority = 95

    def should_trigger(self, perception, world_state, internal_state, hardware_state):
        return False  # no sensors yet

    def execute(self):
        return {"intent": "stop"}
