class CognitionLoop:
    def __init__(self, decision_manager, initiative_manager, context_builder, server_intent_parser):
        self.decision_manager = decision_manager
        self.initiative_manager = initiative_manager
        self.context_builder = context_builder
        self.server_intent_parser = server_intent_parser

    async def run_once(self):
        """
        Single cognition cycle:
        - build context
        - evaluate initiative
        - evaluate decision
        - produce intent
        """
        pass
