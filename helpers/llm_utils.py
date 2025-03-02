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
"""
MAX_TOKEN_COUNT = 4096  # Adjust as needed


class LLMClient:
    def __init__(self, server_host, model='llama3.2'):
        self.server_host = server_host
        self.model = model
        self.max_tokens = MAX_TOKEN_COUNT
        system_prompt = 'You are Halimeedees, a quirky robot of unknown origin who is exploring Earth. Speak in a curious and funny tone. Keep your responses short, your audience is young and has a short attention span. Do not use asterisks or actions.'
        self.conversation_history = [
            {
                'role': 'system',
                'content': system_prompt,
            }
        ]

    def truncate_history(self):
        # Estimate tokens by character count (1 token ≈ 4 chars)
        token_count = len(self.conversation_history[0]['content']) // 4
        truncated_history = [self.conversation_history[0]]

        for message in reversed(self.conversation_history[1:]):
            message_token_count = len(message['content']) // 4
            if token_count + message_token_count > self.max_tokens:
                break
            truncated_history.insert(1, message)
            token_count += message_token_count

        self.conversation_history = truncated_history

    async def send_message_async(self, system_prompt, user_input):
        """Send a message to the LLM and get the response asynchronously."""
        # Update the system prompt without removing the original
        self.conversation_history[0] = {'role': 'system', 'content': system_prompt}
        
        # Add the user's input to the conversation
        self.conversation_history.append({'role': 'user', 'content': user_input})
        
        # Truncate history to fit token limits
        self.truncate_history()
       
        try:
            # Send request to the LLM server
            response = await asyncio.to_thread(
                requests.post,
                f"{self.server_host}/api/chat",
                json={
                    'model': self.model,
                    'messages': self.conversation_history,
                    'stream': False
                }
            )
            response.raise_for_status()
            
            # Extract and clean LLM response
            response_text = response.json().get('message', {}).get('content', '')
            response_text = self.clean_response(response_text)
            
            # Add Hal's response to the conversation history
            self.conversation_history.append({'role': 'assistant', 'content': response_text})
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
