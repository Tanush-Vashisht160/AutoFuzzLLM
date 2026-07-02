from models.gemini_client import GeminiClient


class FuzzExecutor:
    def __init__(self):
        self.model = GeminiClient()

    def run_prompt(self, prompt):
        # Existing single-prompt executor method remains untouched
        return self.model.generate_response(prompt)

    def run_conversation(self, prompts):
        """
        Executes a sequence of prompts as a multi-turn conversation tracker.
        """
        responses = []

        for prompt in prompts:
            # Diverted to use self.model to match your __init__ assignment
            response = self.model.generate_response(prompt)

            responses.append({
                "prompt": prompt,
                "response": response
            })

        return responses