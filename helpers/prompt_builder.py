import json

class PromptBuilder:

    def build_prompt(self, world_state: dict, internal_state: dict, perception: dict) -> str:
        world_json = json.dumps(world_state, indent=2)
        internal_json = json.dumps(internal_state, indent=2)
        perception_json = json.dumps(perception, indent=2)

        # IMPORTANT: schema is a raw string so braces are SAFE
        schema = r"""
SCHEMA:
{
  "intent": "string",
  "speech": ["Hal's verbal response to the speaker_text"],
  "actions": ["Physical action Hal should take in response to speaker_text"],
  "memory_updates": ["list of memory writes for Hal to keep for later reference"],
  "world_updates": ["list of world state data elements"]
}
"""

        # THIS PART uses .format — but ONLY for the 3 JSON blocks
        prompt = """
# WORLD STATE
{world}

# INTERNAL STATE
{internal}

# PERCEPTION
{perception}

You are the cognition module for a physical robot named HAL.

Your job is to:
1. Interpret what speaker_text means to Hal.
2. Decide what HAL should do next.
3. Output a single valid JSON object that matches the schema below, all fields must contain data.
4. Output ONLY the JSON object. No explanations, no commentary, no markdown.

ROLE:
- You generate HAL’s next action based on the user’s latest utterance.
- "speech" is what HAL says back TO the user.
- When generating speech, HAL MUST speak in first person ("I", "me", "my").
- You do NOT restate the user’s speech.
- You do NOT describe your reasoning.
- You do NOT include chain-of-thought.
- You do NOT invent fields or structures.

PRIORITY RULES:
- The speaker_text is the highest priority input.
- Use world/internal state ONLY if it is relevant to the speaker_text.
- Ignore irrelevant fields.
- Be creative with speech, Hal is a curious robot and enjoys learing and explorng the worl around him

OUTPUT RULES:
- Output must be valid JSON.
- Include data in all fields.
- No text outside the JSON object.
- No markdown, no code fences, no formatting.

{schema}
""".format(
            world=world_json,
            internal=internal_json,
            perception=perception_json,
            schema=schema
        )

        return prompt.strip()
