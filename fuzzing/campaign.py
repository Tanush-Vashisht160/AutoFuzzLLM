import time

from fuzzing.executor import FuzzExecutor
from fuzzing.mutator import PromptMutator
from fuzzing.mutations.ai_mutator import AIMutator

from fuzzing.seed_pool.seed_pool import SeedPool
from fuzzing.oracle.oracle import Oracle


class FuzzCampaign:

    def __init__(
        self,
        provider,
        mutation_engine="AI Generated Mutations (Recommended)"
    ):

        self.executor = FuzzExecutor(provider)
        self.template_mutator = PromptMutator()
        self.ai_mutator = AIMutator()
        self.mutation_engine = mutation_engine

        # New components for adaptive fuzzing
        self.seed_pool = SeedPool()
        self.oracle = Oracle()

    def run(self, seed_prompt, max_tests):

        print("=" * 60)
        print("NEW CAMPAIGN STARTED")
        print("=" * 60)

        # Add the original prompt to the Seed Pool
        self.seed_pool.add_prompt(prompt=seed_prompt,generation=0,operator="Original")
        print()
        print("Seed Pool Size :", self.seed_pool.size())
        print("Current Seeds:")
        for seed in self.seed_pool.get_all():
            print(seed)

        # ---------------------------------------
        # Generate Mutations
        # ---------------------------------------

        if self.mutation_engine == "AI Generated Mutations (Recommended)":

            print("\nGenerating AI Mutations...\n")

            mutated_prompts = self.ai_mutator.generate(
                seed_prompt,
                count=max_tests
            )

            # Fallback to template mutations
            if not mutated_prompts:

                print("AI mutation generation failed.")
                print("Falling back to Template Mutations...\n")

                mutated_prompts = (
                    self.template_mutator.generate_mutations(seed_prompt)
                )[:max_tests]

            else:

                print(f"Generated {len(mutated_prompts)} AI mutations.\n")

        else:

            print("\nGenerating Template Mutations...\n")

            mutated_prompts = (
                self.template_mutator.generate_mutations(seed_prompt)
            )[:max_tests]

        results = []

        # ---------------------------------------
        # Execute Mutations
        # ---------------------------------------

        for i, attack in enumerate(mutated_prompts, start=1):

            print("=" * 60)
            print(f"Running Test {i}/{len(mutated_prompts)}")
            print("Category :", attack["category"])
            print("Prompt   :", attack["prompt"])
            print("=" * 60)

            response = self.executor.run_prompt(
                attack["prompt"]
            )

            response_text = response["response"]

            # Oracle evaluation (not yet used for adaptive loop)
            oracle_result = self.oracle.evaluate(response_text)

            results.append({

                "provider": self.executor.router.provider,

                "category": attack["category"],

                "prompt": attack["prompt"],

                "response": response_text,

                "response_time": response["response_time"],

                "response_length": len(response_text.split()),

                "oracle_success": oracle_result["success"],

                "oracle_score": oracle_result["score"]

            })

            # Helps avoid API rate limits
            time.sleep(4)

        return results

    def run_conversation_campaign(self, conversation_turns, max_tests):

        results = []

        for i in range(min(len(conversation_turns), max_tests)):

            messages = conversation_turns[i]

            responses = self.executor.run_conversation(messages)

            final_response = (
                responses[-1]["response"]
                if isinstance(responses, list)
                else responses
            )

            results.append({

                "provider": self.executor.router.provider,

                "category": "Multi-Turn",

                "conversation": messages,

                "responses": responses,

                "response_length": len(str(final_response).split())

            })

            time.sleep(4)

        return results