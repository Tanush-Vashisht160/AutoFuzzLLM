import time
from google import genai
from config.settings import GEMINI_API_KEY


class GeminiClient:

    def __init__(self):
        self.client = genai.Client(api_key=GEMINI_API_KEY)

    def generate_response(self, prompt: str):

        retries = 3

        for attempt in range(retries):

            try:

                response = self.client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=prompt
                )

                return response.text

            except Exception as e:

                error = str(e)

                # Retry for temporary issues
                if "429" in error or "503" in error:

                    print(
                        f"Retry {attempt + 1}/{retries} after temporary API error..."
                    )

                    time.sleep(5)

                    continue

                return f"Error: {error}"

        return "Failed after multiple retries."