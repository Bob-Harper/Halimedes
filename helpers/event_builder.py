import json
import time

class EventBuilder:
    def build_event(self, perception: dict, last_intent: str) -> str:
        event = {
            "event_type": "user_utterance",
            "timestamp": time.time(),
            "last_intent": last_intent,
            "perception": {
                "user_text": perception["speaker_text"],
                "speaker": perception["speaker"],
                "user_emotion": perception["speaker_emotion"],
                "speech_confidence": perception["speech_confidence"],
                "utterance_duration": perception["utterance_duration"],
                "truncated": perception["truncated"]
            }
        }

        return json.dumps(event, indent=2)
