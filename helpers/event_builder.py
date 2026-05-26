class EventBuilder:
    def build_event(self, perception: dict, working_memory=None):
        """
        Normalize perception + working memory into a clean structure
        for the PromptBuilder to transform into message-array format.
        """

        # Extract the actual user text (the thing the model responds to)
        user_text = perception.get("speaker_text", "") or ""

        event = {
            "user_text": user_text,
            "perception": perception,          # full snapshot, not truncated
            "working_memory": working_memory or []
        }

        return event
