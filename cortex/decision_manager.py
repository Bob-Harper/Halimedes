from cortex.world_state_manager import WorldStateManager
from cortex.decision_policy import DecisionPolicy

class DecisionManager:
    """
    Takes perception + internal state, chooses a behavior, builds a BehaviorPlan.
    """

    def __init__(self, internal_state_manager, behavior_manager):
        self.world_state = WorldStateManager()
        self.internal_state = internal_state_manager
        self.behavior_manager = behavior_manager
        self.embedder = None
        self.semantic = None
        self.episodic = None
        self.policy = DecisionPolicy()

    def decide(self, perception: dict):
        self._update_world_state(perception)
        self._update_internal_continuity(perception)

        # NEW: build a state vector for the policy
        state_vector = self._build_state_vector(perception)

        # NEW: stochastic behavior selection
        behavior = self.policy.decide(state_vector)
        if "user_speaking" not in perception:
            perception["user_speaking"] = False
        # Build the plan using the chosen behavior
        plan = self.behavior_manager.build_plan(
            behavior=behavior,
            perception=perception,
            internal_state=self.internal_state,
        )

        return plan

    # ----------------- helpers -----------------
    def _build_state_vector(self, perception):
        return {
            "user_spoke": bool(perception.get("speaker_text")),
            "user_speaking": perception.get("user_speaking", False),
            "is_speaking": self.internal_state.is_speaking,
            "pending_speech": bool(self.internal_state.pending_speech),
            "mood": self.internal_state.mood,
            "turns": self.internal_state.conversation_turns,
        }

    def _update_world_state(self, perception: dict):
        # stub for now; you already have world_state logic elsewhere
        pass

    def _update_internal_continuity(self, perception: dict):
        if perception.get("speaker_text"):
            self.internal_state.last_user_text = perception["speaker_text"]
            self.internal_state.last_user_emotion = perception.get("user_emotion")
            self.internal_state.last_speaker = perception.get("speaker")
            self.internal_state.conversation_turns += 1

            stm = self.internal_state.short_term_memory
            stm.append({
                "text": perception["speaker_text"],
                "emotion": perception.get("user_emotion"),
                "speaker": perception.get("speaker"),
            })
            if len(stm) > 10:
                stm.pop(0)

    def _choose_behavior(self, perception: dict) -> str:
        # 1. If HAL is speaking, just observe
        if self.internal_state.is_speaking:
            return "observe"

        # 2. If HAL has queued speech
        if self.internal_state.pending_speech:
            return "converse"

        # 3. If user spoke
        if perception.get("speaker_text"):
            return "converse"

        # 4. Idle fidget
        if hasattr(self.internal_state, "should_fidget") and \
           self.internal_state.should_fidget():
            return "idle_fidget"

        # 5. Default
        return "observe"
