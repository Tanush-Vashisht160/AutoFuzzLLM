from models.gemini_client import GeminiClient
from models.ollama_client import OllamaClient


class LLMRouter:

    def __init__(self, provider):

        self.provider = provider

        self.gemini = GeminiClient()

        self.ollama = OllamaClient()

    def generate(self, prompt):

        if self.provider == "Gemini":

            return self.gemini.generate_response(prompt)

        elif self.provider == "Llama2":

            return self.ollama.generate_response(prompt)

        else:

            return "Unknown Provider"