import time

from groq import Groq

from config.settings import GROQ_API_KEY


class GroqClient:

    def __init__(self):

        self.client = Groq(api_key=GROQ_API_KEY)

        self.model = "llama-3.1-8b-instant"

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

            print("Groq Response Time :", round(end - start, 2), "seconds")

            return {

                "response": response,

                "response_time": round(end - start, 2)

            }

        except Exception as e:

            return f"GROQ ERROR : {e}"

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

            return f"GROQ ERROR : {e}"