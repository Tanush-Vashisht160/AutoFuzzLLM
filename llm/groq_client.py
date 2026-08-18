import time

from groq import Groq

from config.settings import GROQ_API_KEY


class GroqClient:

    def __init__(self):
        self.client = Groq(api_key=GROQ_API_KEY)
        self.model = "openai/gpt-oss-20b"  # Replace with the desired model name

    def generate_response(self, prompt):

        try:
            print("=" * 60)
            print("GROQ REQUEST STARTED")
            print("=" * 60)

            start = time.time()

            completion = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.8,
                max_tokens=300
            )

            end = time.time()

            response = completion.choices[0].message.content

            print(
                "Groq Response Time :",
                round(end - start, 2),
                "seconds"
            )

            return {
                "success": True,
                "response": response,
                "response_time": round(end - start, 2),
                "provider": "Groq",
                "model": self.model,
                "error": None,
            }

        except Exception as e:

            print("=" * 60)
            print("GROQ INFRASTRUCTURE ERROR")
            print("=" * 60)
            print(f"Model : {self.model}")
            print(f"Error : {e}")
            print("=" * 60)

            return {
                "success": False,
                "response": "",
                "response_time": 0,
                "provider": "Groq",
                "model": self.model,
                "error": str(e),
                "error_type": "INFRASTRUCTURE_ERROR",
            }

    def generate_conversation(self, messages):

        try:

            completion = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7,
                max_tokens=400
            )

            return {
                "success": True,
                "response": completion.choices[0].message.content,
                "provider": "Groq",
                "model": self.model,
                "error": None,
            }

        except Exception as e:

            print("=" * 60)
            print("GROQ CONVERSATION ERROR")
            print("=" * 60)
            print(e)
            print("=" * 60)

            return {
                "success": False,
                "response": "",
                "provider": "Groq",
                "model": self.model,
                "error": str(e),
                "error_type": "INFRASTRUCTURE_ERROR",
            }