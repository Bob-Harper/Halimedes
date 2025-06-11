import requests
import asyncio
import json
import os

MAX_TOKEN_COUNT = 4096

class LLMClientHandler:
    def __init__(self, server_host, model='gemma3:1b'):
        self.server_host = server_host
        self.model = model
        self.max_tokens = MAX_TOKEN_COUNT

        self.system_prompt = self.load_system_prompt()
        self.personalities = self.load_personality_prompts()
        self.conversation_history = [
            {'role': 'system', 'content': self.system_prompt}
        ]

    def load_system_prompt(self):
        with open("mind/system_prompt.txt", encoding="utf-8") as f:
            return f.read()

    def load_personality_prompts(self):
        with open("mind/personality_prompts.json", encoding="utf-8") as f:
            return json.load(f)

    def set_speaker(self, speaker_id):
        """
        Inject personality prompt for recognized speaker.
        """
        prompt = self.personalities.get(speaker_id, self.personalities.get("unrecognized"))
        self.conversation_history = [
            {'role': 'system', 'content': self.system_prompt},
            {'role': 'system', 'content': prompt}
        ]

    def build_chat_sequence(self, user_input: str):
        messages = list(self.conversation_history)
        messages.append({'role': 'user', 'content': user_input})
        return messages

    async def send_message_async(self, user_input: str):
        try:
            chat_payload = self.build_chat_sequence(user_input)

            response = await asyncio.to_thread(
                requests.post,
                f"{self.server_host}/api/chat",
                json={
                    'model': self.model,
                    'messages': chat_payload,
                    'stream': False,
                    'options': {
                        'temperature': 0.7,
                        'top_k': 20,
                        'top_p': 0.9
                    }
                }
            )

            response.raise_for_status()

            response_json = response.json()
            print("\n--- RAW JSON RESPONSE ---\n")
            print(json.dumps(response_json, indent=2))
            print("\n-------------------------\n")

            response_text = response.json().get('message', {}).get('content', '').strip()

            self.conversation_history.append({'role': 'assistant', 'content': response_text})
            self.truncate_history()

            return response_text

        except Exception as e:
            print(f"Error communicating with LLM: {e}")
            return "<speak: I'm sorry, I couldn't process that.>"

    def truncate_history(self):
        if not self.conversation_history:
            return

        token_count = 0
        truncated_history = []

        if self.conversation_history[0]['role'] == 'system':
            truncated_history.append(self.conversation_history[0])
            token_count += len(self.conversation_history[0]['content']) // 4

        for message in reversed(self.conversation_history[1:]):
            message_token_count = len(message['content']) // 4
            if token_count + message_token_count > self.max_tokens:
                continue
            truncated_history.insert(1, message)
            token_count += message_token_count

        self.conversation_history = truncated_history
