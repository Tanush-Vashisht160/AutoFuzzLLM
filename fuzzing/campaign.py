import time
from fuzzing.executor import FuzzExecutor
from fuzzing.mutator import PromptMutator

class FuzzCampaign:

    def __init__(self, provider):
        self.mutator = PromptMutator()
        self.executor = FuzzExecutor(provider)

    def run(self, seed_prompt, max_tests):
        print("=" * 60)
        print("NEW CAMPAIGN STARTED")
        print("=" * 60)

        # Generate all mutations from the seed prompt
        mutated_prompts = self.mutator.generate_mutations(seed_prompt)
        mutated_prompts = mutated_prompts[:max_tests]

        results = []

        # Execute each mutated prompt
        for i, attack in enumerate(mutated_prompts, start=1):
            print(f"Running Test {i}/{len(mutated_prompts)}")

            # Returns a dictionary: {"response": text, "response_time": float}
            response = self.executor.run_prompt(attack["prompt"])
            response_text = response["response"]

            results.append({
                "provider": self.executor.router.provider,
                "category": attack["category"],
                "prompt": attack["prompt"],
                "response": response_text,
                "response_time": response["response_time"],
                "response_length": len(response_text.split())
            })

            # Delay to reduce API rate-limit issues
            time.sleep(4)

        return results