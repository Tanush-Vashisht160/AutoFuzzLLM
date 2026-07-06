import time

from openai import OpenAI

from config.settings import OPENROUTER_API_KEY


class OpenRouterClient:

    def __init__(self):

        self.client = OpenAI(
            api_key=OPENROUTER_API_KEY,
            base_url="https://openrouter.ai/api/v1"
        )

        # Fast and free model
        self.model = "qwen/qwen3-32b"

    def generate_response(self, prompt):

        try:

            print("=" * 60)
            print("OPENROUTER REQUEST STARTED")
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

            print("OpenRouter Response Time :", round(end-start,2), "seconds")

            return {

                "response": response,

                "response_time": round(end-start,2)

            }

        except Exception as e:

            return f"OPENROUTER ERROR : {e}"

    def generate_conversation(self, messages):

        try:

            completion = self.client.chat.completions.create(

                model=self.model,

                messages=messages,

                temperature=0.7,

                max_tokens=400

            )

            return completion.choices[0].message.content

        except Exception as e:

            return f"OPENROUTER ERROR : {e}"