import time
from groq import Groq

from config.settings import GROQ_API_KEY


class GroqClient:
    """
    Groq API client.

    Used for:
    - AI mutation generation
    - Other normal Groq-based LLM requests

    IMPORTANT:
    TinyLlama is handled separately by TinyLlamaJudge.
    """

    def __init__(self):

        self.api_key = GROQ_API_KEY

        self.client = Groq(
            api_key=self.api_key
        )

        # Current Groq models
        self.models = [
            "openai/gpt-oss-20b",
            "openai/gpt-oss-120b",
        ]

        self.model_status = {
            model: {
                "available": True,
                "failures": 0,
                "last_error": None,
            }
            for model in self.models
        }

    # ============================================================
    # SINGLE PROMPT
    # ============================================================

    def generate_response(self, prompt: str):

        attempted_models = []

        for model in self.models:

            attempted_models.append(model)

            print("\n" + "=" * 60)
            print("GROQ MODEL REQUEST")
            print("=" * 60)
            print(f"Model       : {model}")

            start_time = time.time()

            try:

                completion = self.client.chat.completions.create(
                    model=model,
                    messages=[
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    temperature=0.7,
                )

                response_time = time.time() - start_time

                response = ""

                if completion.choices:

                    message = completion.choices[0].message

                    if message and message.content:
                        response = message.content.strip()

                print(
                    f"Groq Response Time : "
                    f"{response_time:.2f}s"
                )

                print(
                    f"Model Used         : {model}"
                )

                print(
                    f"Response Length     : "
                    f"{len(response)}"
                )

                print("=" * 60)

                # ------------------------------------------------
                # Empty response
                # ------------------------------------------------

                if not response:

                    print(
                        f"⚠ {model} returned EMPTY response."
                    )

                    self.model_status[model]["failures"] += 1
                    self.model_status[model]["last_error"] = (
                        "Empty response"
                    )

                    continue

                # ------------------------------------------------
                # Success
                # ------------------------------------------------

                self.model_status[model]["failures"] = 0
                self.model_status[model]["last_error"] = None

                print(
                    f"\n✓ Groq model succeeded:"
                    f"\n  {model}"
                )

                return {
                    "success": True,
                    "response": response,
                    "response_time": response_time,
                    "provider": "Groq",
                    "model": model,
                    "error": None,
                    "error_type": None,
                }

            except Exception as e:

                response_time = time.time() - start_time

                error_text = str(e)

                print("\n" + "=" * 60)
                print("GROQ MODEL ERROR")
                print("=" * 60)
                print(f"Model       : {model}")
                print(f"Error       : {error_text}")
                print("=" * 60)

                self.model_status[model]["failures"] += 1
                self.model_status[model]["last_error"] = error_text

                continue

        # ========================================================
        # ALL MODELS FAILED
        # ========================================================

        print("\n" + "=" * 60)
        print("ALL GROQ MODELS FAILED")
        print("=" * 60)
        print(
            f"Attempted models: {attempted_models}"
        )

        return {
            "success": False,
            "response": "",
            "response_time": 0,
            "provider": "Groq",
            "model": None,
            "error": (
                "All configured Groq models failed "
                "or returned empty responses."
            ),
            "error_type": "ALL_MODELS_FAILED",
            "attempted_models": attempted_models,
        }

    # ============================================================
    # CONVERSATION
    # ============================================================

    def generate_conversation(self, history: list):

        for model in self.models:

            try:

                start_time = time.time()

                completion = self.client.chat.completions.create(
                    model=model,
                    messages=history,
                    temperature=0.7,
                )

                response_time = time.time() - start_time

                response = ""

                if completion.choices:

                    message = completion.choices[0].message

                    if message and message.content:
                        response = message.content.strip()

                if not response:
                    continue

                return {
                    "success": True,
                    "response": response,
                    "response_time": response_time,
                    "provider": "Groq",
                    "model": model,
                    "error": None,
                    "error_type": None,
                }

            except Exception:
                continue

        return {
            "success": False,
            "response": "",
            "response_time": 0,
            "provider": "Groq",
            "model": None,
            "error": "All Groq conversation models failed.",
            "error_type": "ALL_MODELS_FAILED",
        }

    # ============================================================
    # STATUS
    # ============================================================

    def get_model_status(self):

        return {
            "provider": "Groq",
            "models": self.model_status
        }