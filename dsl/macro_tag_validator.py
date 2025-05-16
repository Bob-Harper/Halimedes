from difflib import get_close_matches

class MacroTagValidator:
    VALID_TAG_TYPE = ['sound', 'action', 'gaze', 'face', 'speak']
    VALID_ACTIONS = ['expressive', 'subtle', 'full-body']
    VALID_GAZE = ['left', 'right', 'up', 'down', 'center', 'wander']

    @staticmethod
    def closest_match(word, valid_list):
        matches = get_close_matches(word.lower(), valid_list, n=1, cutoff=0.6)
        return matches[0] if matches else valid_list[0]  # fallback to first valid

    @classmethod
    def validate_tag_type(cls, tag: str):
        return cls.closest_match(tag, cls.VALID_TAG_TYPE)

    @classmethod
    def validate_action(cls, tag: str):
        return cls.closest_match(tag, cls.VALID_ACTIONS)

    @classmethod
    def validate_gaze(cls, tag: str):
        return cls.closest_match(tag, cls.VALID_GAZE)
    