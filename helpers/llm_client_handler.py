import requests
import asyncio
import re

"""
MAX_TOKEN_COUNT represents the character count limit for conversation history.
- The actual token count is approximately one-fourth the character count.
- Smaller values result in faster response times but less memory context.
- Larger values retain more context but increase response time and resource usage.
For quick testing, use a smaller value (e.g., 512). For production or complex tasks,
consider increasing this value (e.g., 2048) to enhance conversational memory.
These models max out high but will signicicantly reduce speed of response.
gemma3:4b                          a2af6cc3eb7f    3.3 GB    128k context window Multimodal
gemma3:1b                          8648f39daa8f    815 MB    32k context window
llama3.2:latest                    a80c4f17acd5    2.0 GB    128k context window
"""
MAX_TOKEN_COUNT = 4096  # Adjust as needed


class LLMClientHandler:
    def __init__(self, server_host, model='gemma3:1b'):
        self.server_host = server_host
        self.model = model
        self.max_tokens = MAX_TOKEN_COUNT
        with open("helpers/instruction_prompt.txt", encoding="utf-8") as f:
            system_prompt = f.read()
        self.conversation_history = [
            {
                'role': 'system',
                'content': system_prompt,
            }
        ]

    def build_chat_sequence(self, user_input: str):
        """
        Returns the list of messages:
        1) the original system prompt (preserved in conversation_history[0]),
        2) any prior user/assistant turns,
        3) the new user turn.
        """
        # Start with whatever is already in conversation_history
        messages = list(self.conversation_history)

        # Append the new user turn (with speaker prefix in content)
        messages.append({
            'role': 'user',
            'content': user_input
        })

        return messages

        
    async def send_message_async(self, user_input: str):
        """
        Send a message to the LLM and get the response asynchronously.
        user_input should already include the speaker prefix
        """
        try:
            # Build chat payload from history + this one user turn
            chat_payload = self.build_chat_sequence(user_input)
            # print(f"[DEBUG] llm_client_handler.py self.server_host: {self.server_host}")
            response = await asyncio.to_thread(
                requests.post,
                f"{self.server_host}/api/chat",
                json={
                    'model':    self.model,
                    'messages': chat_payload,
                    'stream':   False,
                    'options': {
                        'temperature': 0.8,
                        'top_k':       20,
                        'top_p':       0.9
                    }
                }
            )
            response.raise_for_status()

            response_text = response.json().get('message', {}).get('content', '')
            response_text = self.clean_response(response_text)

            # record assistant turn
            self.conversation_history.append({
                'role': 'assistant',
                'content': response_text
            })

            self.truncate_history()
            return response_text

        except Exception as e:
            print(f"Error communicating with LLM: {e}")
            return "I'm sorry, I couldn't process that."

    @staticmethod
    def clean_response(text):
        # Remove all *text* patterns (including things like *stunned silence*)
        text = re.sub(r"\*.*?\*", "", text)
        # Define replacements (all in lowercase for matching)
        replacements = {
            "brrr": "burr",
            "debug": "deebug",
            "hehe": "Heh Heh",
            "preload": "preeload",
            "sci-fi": "sigh-fye",
            "aww": "awe",
            "hmmm": "hmm",
        }

        # Function to match case dynamically
        def case_sensitive_replace(match):
            word = match.group(0)
            replacement = replacements[word.lower()]  # Lookup in lowercase

            # Preserve original case:
            if word.istitle():  # Capitalized (e.g., "Brrr")
                return replacement.capitalize()
            elif word.isupper():  # Fully uppercase (e.g., "BRRR")
                return replacement.upper()
            else:  # All lowercase (e.g., "brrr")
                return replacement

        # Use regex to replace only whole words (case-insensitive)
        pattern = re.compile(r'\b(' + '|'.join(re.escape(key) for key in replacements.keys()) + r')\b', re.IGNORECASE)
        cleaned_text = pattern.sub(case_sensitive_replace, text)

        return cleaned_text.strip()

    def truncate_history(self):
        """Smarter history trimming based on max token count."""
        if not self.conversation_history:
            return

        token_count = 0
        truncated_history = []

        # Always preserve the system prompt first
        if self.conversation_history[0]['role'] == 'system':
            truncated_history.append(self.conversation_history[0])
            token_count += len(self.conversation_history[0]['content']) // 4

        # Add messages until limit is hit
        for message in reversed(self.conversation_history[1:]):
            message_token_count = len(message['content']) // 4
            if token_count + message_token_count > self.max_tokens:
                continue  # Skip this message (too big)
            truncated_history.insert(1, message)
            token_count += message_token_count

        self.conversation_history = truncated_history
