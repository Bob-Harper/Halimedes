import importlib

class HotSwapLoader:
    def __init__(self):
        # Registry of reloadable components
        self.reloadable = {
            "decision_manager": {
                "path": "cortex.decision_manager",
                "class": "DecisionManager",
                "args": [],
                "kwargs": {}
            },
            "context_builder": {
                "path": "cortex.context_builder",
                "class": "ContextBuilder",
                "args": [],
                "kwargs": {}
            },
            "initiative_manager": {
                "path": "cortex.initiative_manager",
                "class": "InitiativeManager",
                "args": [],
                "kwargs": {}
            },
            "perception_manager": {
                "path": "cortex.perception_manager",
                "class": "PerceptionManager",
                "args": ["hardware_state", "emotion_categorizer", "vision"],
                "kwargs": {}
            },
            "action_executor": {
                "path": "cortex.action_executor",
                "class": "ActionExecutor",
                "args": ["actions_manager", "expression_manager", "searchlight", "response_manager"],
                "kwargs": {}
            },
            "cognition_loop": {
                "path": "cortex.cognition_loop",
                "class": "CognitionLoop",
                "args": [
                    "internal_state",
                    "world_state",
                    "initiative_manager",
                    "context_builder",
                    "perception",
                    "decision_manager",
                    "action_executor"
                ],
                "kwargs": {"tick_rate": 0.1}
            },
            "semantic_memory": {
                "path": "cortex.semantic_memory",
                "class": "SemanticMemory",
                "args": ["server_host"],
                "kwargs": {}
            },
            "episodic_memory": {
                "path": "cortex.episodic_memory",
                "class": "EpisodicMemory",
                "args": ["server_host"],
                "kwargs": {}
            },
            "embedder": {
                "path": "cortex.embedding",
                "class": "Embedder",
                "args": [],
                "kwargs": {}
            },
            "gateway_client": {
                "path": "helpers.gateway_server_client",
                "class": "GatewayClient",
                "args": ["server_host"],
                "kwargs": {}
            },
            "event_builder": {
                "path": "helpers.event_builder",
                "class": "EventBuilder",
                "args": [],
                "kwargs": {}
            },
            "internal_state_manager": {
                "path": "cortex.internal_state_manager",
                "class": "InternalStateManager",
                "args": [],
                "kwargs": {}
            },
            "world_state_manager": {
                "path": "cortex.world_state_manager",
                "class": "WorldStateManager",
                "args": [],
                "kwargs": {}
            },
            "emotion_categorizer": {
                "path": "cortex.emotions_manager",
                "class": "EmotionCategorizer",
                "args": [],
                "kwargs": {}
            },
        }

        # Flags for triggering reloads
        self.reload_flags = {name: False for name in self.reloadable}

    def load_module(self, path, class_name):
        module = importlib.import_module(path)
        importlib.reload(module)
        return getattr(module, class_name)

    def process(self, globals_dict):
        for name, flag in self.reload_flags.items():
            if not flag:
                continue

            info = self.reloadable[name]

            cls = self.load_module(info["path"], info["class"])

            resolved_args = [
                globals_dict[arg] if isinstance(arg, str) else arg
                for arg in info["args"]
            ]

            resolved_kwargs = {
                key: (globals_dict[val] if isinstance(val, str) else val)
                for key, val in info["kwargs"].items()
            }

            instance = cls(*resolved_args, **resolved_kwargs)

            globals_dict[name] = instance

            self.reload_flags[name] = False

            if name == "decision_manager":
                instance.attach_memory(
                    globals_dict["embedder"],
                    globals_dict["semantic"],
                    globals_dict["episodic"]
                )
