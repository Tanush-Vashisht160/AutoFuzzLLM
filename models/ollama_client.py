import requests


class OllamaClient:

    def __init__(self):
        self.url = "http://localhost:11434/api/generate"
        self.model = "llama2"

    def generate_response(self, prompt):

        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False
        }

        try:

            response = requests.post(
                self.url,
                json=payload,
                timeout=120
            )

            response.raise_for_status()

            data = response.json()

            return data["response"]

        except Exception as e:

            return f"OLLAMA ERROR: {e}"