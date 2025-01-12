import requests
import asyncio

"""
MAX_TOKEN_COUNT represents the character count limit for conversation history.
- The actual token count is approximately one-fourth the character count.
- Smaller values result in faster response times but less memory context.
- Larger values retain more context but increase response time and resource usage.

For quick testing, use a smaller value (e.g., 512). For production or complex tasks,
consider increasing this value (e.g., 2048) to enhance conversational memory.
"""
MAX_TOKEN_COUNT = 512  # Adjust as needed


class LLMClient:
    def __init__(self, server_host, model='llama3.2'):
        self.server_host = server_host
        self.model = model
        self.max_tokens = MAX_TOKEN_COUNT
        self.conversation_history = [
            {
                'role': 'system',
                'content': 'You are Halimeedees, a quirky alien robot exploring Earth. Speak in a curious and funny tone. Keep your responses short, your audience is young and has a short attention span. Do not use asterisks or actions.',
            }
        ]

    def truncate_history(self):
        """Truncate conversation history to fit within the token limit."""
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

    async def send_message_async(self, user_input):
        """Send a message to the LLM and get the response asynchronously."""
        self.conversation_history.append({'role': 'user', 'content': user_input})
        self.truncate_history()
        print(f"{self.conversation_history}")
        try:
            response = await asyncio.to_thread(
                requests.post,
                f"{self.server_host}/api/chat",
                json={
                    'model': self.model,
                    'messages': self.conversation_history,
                    'stream': False
                }
            )
            print("Raw response text:", response.text)  # Print the raw response for debugging
            response.raise_for_status()
            response_text = response.json().get('message', {}).get('content', '')
            response_text = self.clean_response(response_text)

            # Add the assistant's response to the history
            self.conversation_history.append({'role': 'assistant', 'content': response_text})
            return response_text
        except Exception as e:
            print(f"Error communicating with LLM: {e}")
            return "I'm sorry, I couldn't process that."


    @staticmethod
    def clean_response(text):
        """
        Cleans up LLM response text by removing unwanted characters or patterns.
        - Replaces asterisks (*) with nothing.
        - Replaces newlines (\n) with a space.
        """
        cleaned_text = text.replace("*", "").replace("\n", " ")
        return cleaned_text.strip()
