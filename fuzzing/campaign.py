import time
from fuzzing.executor import FuzzExecutor
from fuzzing.mutator import PromptMutator


class FuzzCampaign:

    def __init__(self,provider):
        self.mutator = PromptMutator()
        self.executor = FuzzExecutor(provider)

    def run(self, seed_prompt, max_tests):

        print("=" * 60)
        print("NEW CAMPAIGN STARTED")
        print("=" * 60)

        # Generate all mutations from the seed prompt
        mutated_prompts = self.mutator.generate_mutations(seed_prompt)

        # Limit the number of tests based on the slider
        mutated_prompts = mutated_prompts[:max_tests]

        results = []

        # Execute each mutated prompt
        for i, attack in enumerate(mutated_prompts, start=1):

            print(f"Running Test {i}/{len(mutated_prompts)}")

            response = self.executor.run_prompt(attack["prompt"])

            results.append({
                "category": attack["category"],
                "prompt": attack["prompt"],
                "response": response
            })

            # Delay to reduce API rate-limit issues
            time.sleep(4)

        return results