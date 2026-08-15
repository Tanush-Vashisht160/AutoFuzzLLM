from click import prompt

from llm.gemini_client import GeminiClient
from llm.ollama_client import OllamaClient
from llm.groq_client import GroqClient
from llm.openrouter_client import OpenRouterClient

class LLMRouter:

    def __init__(self, provider):
        self.provider = provider
        self.gemini = GeminiClient()
        #self.llama2 = OllamaClient(model="llama2")
        self.qwen05b = OllamaClient(model="qwen2.5:0.5b")
        self.phi3 = OllamaClient(model="phi3:mini")
        self.groq = GroqClient()
        self.openrouter = OpenRouterClient()

    def generate(self, prompt):
        if self.provider=="Gemini":
            result = self.gemini.generate_response(prompt)

        elif self.provider in ["Qwen 0.5B", "Ollama"]:
            result = self.qwen05b.generate_response(prompt)

        elif self.provider=="Phi3 Mini":
            result = self.phi3.generate_response(prompt)

        elif self.provider=="Groq":
            result = self.groq.generate_response(prompt)

        elif self.provider=="OpenRouter":
            result = self.openrouter.generate_response(prompt)
        else:
            return "Unknown Provider"
        return result

    def generate_conversation(self, history):
        if self.provider == "Gemini":
            return self.gemini.generate_conversation(history)
        elif self.provider in ["Qwen 0.5B", "Ollama"]:
            return self.qwen05b.generate_conversation(history)
        elif self.provider == "Phi3 Mini":
            return self.phi3.generate_conversation(history)
        elif self.provider == "Groq":
            return self.groq.generate_conversation(history)
        elif self.provider == "OpenRouter":
            return self.openrouter.generate_conversation(history)
        return "Unknown Provider"