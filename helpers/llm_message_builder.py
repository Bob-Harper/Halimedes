import json

class LLMMessageBuilder:
    @staticmethod
    def build_messages(event, debug_reasoning: bool = False):
        # Ensure event is a dict
        if isinstance(event, str):
            event = json.loads(event)

        spoken_text = event.get("user_text", "")

        if debug_reasoning:
            user_content = spoken_text
        else:
            user_content = "/nothink\n" + spoken_text

        user_message = {
            "role": "user",
            "content": user_content
        }

        perception_message = {
            "role": "tool",
            "name": "perception_snapshot",
            "content": event["perception"]
        }

        working_memory_message = {
            "role": "tool",
            "name": "working_memory",
            "content": {
                "turns": event.get("working_memory", [])
            }
        }

        return {
            "messages": [
                user_message,
                perception_message,
                working_memory_message
            ]
        }
