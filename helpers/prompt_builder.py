import json

class PromptBuilder:

    def build_prompt(self, world_state: dict, internal_state: dict, perception: dict) -> str:
        world_json = json.dumps(world_state, indent=2)
        internal_json = json.dumps(internal_state, indent=2)
        perception_json = json.dumps(perception, indent=2)

        prompt = f"""
WORLD_STATE:
{world_json}

INTERNAL_STATE:
{internal_json}

PERCEPTION:
{perception_json}

INSTRUCTION:
Use the perception and internal state to generate Hal's next intent, speech response, and actions.
I want you to perform a full external‑fetch diagnostic.

1. Fetch https://httpbin.org/uuid and report the UUID.
2. Fetch https://httpbin.org/ip and report the server IP.
3. Fetch https://httpbin.org/headers and report the headers.
4. Fetch https://httpbin.org/get?foo=bar and report the query echo.
5. Fetch https://httpbin.org/anything and summarize the entire response.

You must use tool calls for each step. Do not guess. Retrieve real values.
After each tool call, analyze the result and continue.""".strip()

        return prompt
