from llm.gemini_client import GeminiClient
from llm.groq_client import GroqClient
from llm.ollama_client import OllamaClient
from llm.openrouter_client import OpenRouterClient


class LLMRouter:
    """Central routing layer for managing requests across various LLM providers.

    Preserves provider naming while offering uniform response structures and
    internal fallback handling for supported backends.
    """

    def __init__(self, provider: str):
        self.provider = provider

        # --------------------------------------------------------
        # Cloud LLM Clients
        # --------------------------------------------------------
        self.gemini = GeminiClient()
        self.groq = GroqClient()
        self.openrouter = OpenRouterClient()

        # --------------------------------------------------------
        # Local Ollama LLM Clients
        # --------------------------------------------------------
        self.qwen05b = OllamaClient(model="qwen2.5:0.5b")
        self.phi3 = OllamaClient(model="phi3:mini")

    # ============================================================
    # SINGLE PROMPT GENERATION
    # ============================================================

    def generate(self, prompt: str):
        """Routes a single prompt string to the configured LLM provider.

        Returns a dictionary containing response metadata and success status.
        """
        if self.provider == "Gemini":
            return self.gemini.generate_response(prompt)

        elif self.provider in ["Qwen 0.5B", "Ollama"]:
            return self.qwen05b.generate_response(prompt)

        elif self.provider == "Phi3 Mini":
            return self.phi3.generate_response(prompt)

        elif self.provider == "Groq":
            # Note: GroqClient internally handles automatic model fallback
            return self.groq.generate_response(prompt)

        elif self.provider == "OpenRouter":
            return self.openrouter.generate_response(prompt)

        else:
            return {
                "success": False,
                "response": "",
                "response_time": 0,
                "provider": self.provider,
                "model": None,
                "error": f"Unknown provider: {self.provider}",
                "error_type": "UNKNOWN_PROVIDER",
            }

    # ============================================================
    # CONVERSATIONAL GENERATION
    # ============================================================

    def generate_conversation(self, history: list):
        """Routes conversational message history to the configured LLM provider."""
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

        else:
            return {
                "success": False,
                "response": "",
                "provider": self.provider,
                "model": None,
                "error": f"Unknown provider: {self.provider}",
                "error_type": "UNKNOWN_PROVIDER",
            }

    # ============================================================
    # SYSTEM HEALTH & STATUS
    # ============================================================

    def get_groq_status(self):
        """Exposes health metrics and active model status from GroqClient."""
        return self.groq.get_model_status()