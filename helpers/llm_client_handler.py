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

gemma3:4b                          a2af6cc3eb7f    3.3 GB    2 days ago
gemma3:1b                          8648f39daa8f    815 MB    2 days ago
wizard-vicuna-uncensored:latest    72fc3c2b99dc    3.8 GB    5 months ago
mannix/llava-phi3:iq2_s            e057e6453da9    1.9 GB    6 months ago
tinyllama:latest                   2644915ede35    637 MB    6 months ago
llava-llama3:latest                44c161b1f465    5.5 GB    6 months ago
me/llama3.1-python:latest          74f77feb57b9    5.7 GB    6 months ago
llama3.2:latest                    a80c4f17acd5    2.0 GB    6 months ago
"""
MAX_TOKEN_COUNT = 4096  # Adjust as needed


class LLMClientHandler:
    def __init__(self, server_host, model='tinyllama'):
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

    def build_chat_sequence(self, system_prompt, user_input):
        """
        Builds a structured conversation history for models like Gemma that expect <|user|> / <|assistant|> blocks.
        """
        chat_sequence = []

        # Start with system prompt
        chat_sequence.append({
            'role': 'system',
            'content': system_prompt
        })

        # Replay conversation history
        for message in self.conversation_history:
            chat_sequence.append({
                'role': message['role'],
                'content': message['content']
            })

        # Append new user input
        chat_sequence.append({
            'role': 'user',
            'content': user_input
        })

        return chat_sequence
    
    async def send_message_async(self, system_prompt, user_input):
        """Send a message to the LLM and get the response asynchronously."""
        
        try:
            # Build proper chat sequence
            chat_payload = self.build_chat_sequence(system_prompt, user_input)

            # Send request to the LLM server
            response = await asyncio.to_thread(
                requests.post,
                f"{self.server_host}/api/chat",
                json={
                    'model': self.model,
                    'messages': chat_payload,
                    'stream': False
                }
            )
            response.raise_for_status()
            
            # Extract and clean LLM response
            response_text = response.json().get('message', {}).get('content', '')
            response_text = self.clean_response(response_text)
            
            # Save assistant's reply into history
            self.conversation_history.append({
                'role': 'assistant',
                'content': response_text
            })

            # Truncate history if needed
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
