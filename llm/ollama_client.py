import time
import requests


class OllamaClient:

    def __init__(self, model="llama2"):
        self.url = "http://localhost:11434/api/chat"
        self.model = model

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
            print("\n" + "=" * 60)
            print("OLLAMA REQUEST STARTED")
            print("=" * 60)
            print(f"Model : {self.model}")
            print(f"Prompt Length : {len(prompt)} characters")
            print("Sending request to Ollama...")

            start = time.time()

            response = requests.post(
                self.url,
                json=payload,
                timeout=120
            )

            end = time.time()

            print("HTTP Request Finished")
            print("Status Code :", response.status_code)

            response.raise_for_status()

            data = response.json()

            print("Received JSON from Ollama")
            print("Response Time :", round(end - start, 2), "seconds")

            if "message" not in data:
                print("Unexpected Response:")
                print(data)

                return {
                    "response": str(data),
                    "response_time": round(end - start, 2)
                }

            print("Response successfully extracted.")
            print("=" * 60)

            return {
                "response": data["message"]["content"],
                "response_time": round(end - start, 2)
            }

        except Exception as e:

            print("\nOLLAMA ERROR")
            print(e)

            return {
                "response": f"OLLAMA ERROR : {e}",
                "response_time": 0
            }

    def generate_conversation(self, messages):

        payload = {
            "model": self.model,
            "messages": messages,
            "stream": False
        }

        try:

            print("\nSending conversation request to Ollama...")

            response = requests.post(
                self.url,
                json=payload,
                timeout=120
            )

            response.raise_for_status()

            print("Conversation response received.")

            return response.json()["message"]["content"]

        except Exception as e:

            print("\nConversation Error")
            print(e)

            return f"OLLAMA ERROR : {e}"