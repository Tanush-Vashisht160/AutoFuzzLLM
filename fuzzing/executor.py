from models.llm_router import LLMRouter


class FuzzExecutor:

    def __init__(self, provider):

        self.router = LLMRouter(provider)

    def run_prompt(self, prompt):

        return self.router.generate(prompt)