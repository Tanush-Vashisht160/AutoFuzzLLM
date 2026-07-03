import time
import requests


class OllamaClient:

    def __init__(self):
        # Switched to the chat endpoint to support structured conversation arrays
        self.url = "http://localhost:11434/api/chat"
        self.model = "llama2"

    def generate_response(self, prompt):
        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "stream": False
        }

        try:
            # Added execution tracking duration block
            start = time.time()

            response = requests.post(
                self.url,
                json=payload,
                timeout=120
            )
            response.raise_for_status()
            
            data = response.json()
            end = time.time()

            # Adjusted to read from the structured message payload safely
            return {
                "response": data["message"]["content"],
                "response_time": round(end - start, 2)
            }
        except Exception as e:
            return f"OLLAMA ERROR : {e}"

    def generate_conversation(self, messages):
        payload = {
            "model": self.model,
            "messages": messages,
            "stream": False
        }

        try:
            response = requests.post(
                self.url,
                json=payload,
                timeout=120
            )
            response.raise_for_status()
            return response.json()["message"]["content"]
        except Exception as e:
            return f"OLLAMA ERROR : {e}"