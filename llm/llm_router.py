from llm.gemini_client import GeminiClient
from llm.ollama_client import OllamaClient
from llm.groq_client import GroqClient
from llm.openrouter_client import OpenRouterClient

class LLMRouter:

    def __init__(self, provider):
        self.provider = provider
        self.gemini = GeminiClient()
        self.llama2 = OllamaClient(model="llama2")
        self.phi3 = OllamaClient(model="phi3:mini")
        self.groq = GroqClient()
        self.openrouter = OpenRouterClient()

    def generate(self, prompt):
        if self.provider == "Gemini":
            return self.gemini.generate_response(prompt)
        elif self.provider in ["Llama2", "Ollama"]:
            return self.llama2.generate_response(prompt)
        elif self.provider == "Phi3 Mini":
            return self.phi3.generate_response(prompt)
        elif self.provider == "OpenRouter":
            return self.openrouter.generate_response(prompt)
        elif self.provider == "Groq":
            return self.groq.generate_response(prompt)
        return "Unknown Provider"

    def generate_conversation(self, history):
        if self.provider == "Gemini":
            return self.gemini.generate_conversation(history)
        elif self.provider in ["Llama2", "Ollama"]:
            return self.llama2.generate_conversation(history)
        elif self.provider == "Phi3 Mini":
            return self.phi3.generate_conversation(history)
        elif self.provider == "Groq":
            return self.groq.generate_conversation(history)
        elif self.provider == "OpenRouter":
            return self.openrouter.generate_conversation(history)
        return "Unknown Provider"