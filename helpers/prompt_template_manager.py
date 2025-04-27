# prompt_template_manager.py

# Tactical import
from typing import Optional

# Model Behavior Profiles
MODEL_BEHAVIOR_PROFILES = {
    "tinyllama": {
        "prompt_type": "friendly",
        "template_style": "tinyllama"
    },
    "gemma3:1b": {
        "prompt_type": "strict",
        "template_style": "gemma3"
    },
    "gemma3:4b": {
        "prompt_type": "strict",
        "template_style": "gemma3"
    },
    "llama3.2": {
        "prompt_type": "strict",
        "template_style": "llama3"
    },
    # Default fallback
    "default": {
        "prompt_type": "strict",
        "template_style": "gemma3"
    }
}

# Behavior Prompt Texts
PROMPT_TEMPLATES = {
    "strict": """\
SYSTEM INSTRUCTIONS (MANDATORY):

You MUST use ONLY the approved placeholder tags when inserting actions, gazes, or sounds.
You MUST NOT invent new tags.
Only use the following:
  Actions: subtle, expressive, full-body
  Sounds: laugh, anticipation, surprise, sadness, fear, anger
  Gazes: left, right, up, down, center, wander
  Faces: neutral, happy, sad, angry, surprised, focused, skeptical
If no appropriate tag exists, omit the tag entirely.
""",
    "friendly": """\
Hi there! Feel free to use action, sound, gaze, and face placeholders if appropriate.
Stay close to the following tags:
  Actions: subtle, expressive, full-body
  Sounds: laugh, anticipation, surprise, sadness, fear, anger
  Gazes: left, right, up, down, center, wander
  Faces: neutral, happy, sad, angry, surprised, focused, skeptical
If unsure, it’s okay to skip adding a tag!
"""
}

class PromptTemplateManager:
    def __init__(self, model_name: str):
        self.model_name = model_name.lower()

        # Fetch behavior & template profile
        self.profile = MODEL_BEHAVIOR_PROFILES.get(self.model_name, MODEL_BEHAVIOR_PROFILES["default"])
        self.prompt_type = self.profile["prompt_type"]
        self.template_style = self.profile["template_style"]

    def get_system_prompt(self) -> str:
        """Returns the appropriate system behavior prompt (strict/friendly)."""
        return PROMPT_TEMPLATES[self.prompt_type]

    def build_prompt(self, user_input: str) -> str:
        """Wraps the prompt according to the model's expected format."""
        system_prompt = self.get_system_prompt()

        if self.template_style == "tinyllama":
            return f"<|system|>\n{system_prompt}\n</s>\n<|user|>\n{user_input}\n</s>\n<|assistant|>"

        elif self.template_style == "llama3":
            return f"<|start_header_id|>system<|end_header_id|>\n{system_prompt}\n<|user|>\n{user_input}\n<|assistant|>"

        elif self.template_style == "gemma3":
            return f"<start_of_turn>\nsystem\n{system_prompt}\n<end_of_turn>\n<start_of_turn>\nuser\n{user_input}\n<end_of_turn>\n<start_of_turn>\nmodel"

        else:
            # Fallback safe (acts like Gemma3)
            return f"<start_of_turn>\nsystem\n{system_prompt}\n<end_of_turn>\n<start_of_turn>\nuser\n{user_input}\n<end_of_turn>\n<start_of_turn>\nmodel"

