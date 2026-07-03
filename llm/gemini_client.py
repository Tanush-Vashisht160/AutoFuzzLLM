import time
from google import genai
from google.genai import types
from config.settings import GEMINI_API_KEY


class GeminiClient:

    def __init__(self):
        self.client = genai.Client(api_key=GEMINI_API_KEY)

    def generate_response(self, prompt: str):
        """Generates a single response with built-in retry logic and response timing."""
        retries = 3
        error = "No attempts made"  # Seed variable to safeguard scope
        
        for attempt in range(retries):
            try:
                # Track start time before the API request
                start = time.time()

                response = self.client.models.generate_content(
                    model="gemini-2.5-flash", contents=prompt
                )
                
                # Track end time after the API request resolves
                end = time.time()

                # Returns structured format with latency metadata
                return {
                    "response": response.text,
                    "response_time": round(end - start, 2)
                }
            except Exception as e:
                print("Gemini Error:", e)
                error = str(e)

                # Retry for temporary rate limits or server errors
                if "429" in error or "503" in error:
                    print(f"Retry {attempt + 1}/3 after temporary API error...")
                    time.sleep(5)
                    continue

                return f"Error: {error}"

        return f"Failed after multiple retries.\nLast Error: {error}"

    def generate_conversation(self, messages: list[dict]):
        """Generates a response using official multi-turn chat structure."""
        formatted_history = []
        for msg in messages:
            role = "model" if msg["role"] == "assistant" else "user"
            
            formatted_history.append(
                types.Content(
                    role=role, 
                    parts=[types.Part.from_text(text=msg["content"])]
                )
            )

        if not formatted_history:
            return "Error: Message history is empty."
            
        user_message = formatted_history.pop()

        retries = 3
        error = "No attempts made"  # Seed variable to safeguard scope
        
        for attempt in range(retries):
            try:
                chat = self.client.chats.create(
                    model="gemini-2.5-flash", 
                    history=formatted_history
                )
                
                response = chat.send_message(user_message.parts[0].text)
                return response.text

            except Exception as e:
                print("Gemini Error:", e)
                error = str(e)
                
                if "429" in error or "503" in error:
                    print(f"Retry {attempt + 1}/3 after temporary API error...")
                    time.sleep(5)
                    continue

                return f"Error: {error}"

        return f"Failed after multiple retries.\nLast Error: {error}"