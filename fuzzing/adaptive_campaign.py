import time

from fuzzing.executor import FuzzExecutor
from fuzzing.mutations.ai_mutator import AIMutator
from fuzzing.seed_pool.seed_pool import SeedPool
from fuzzing.oracle.oracle import Oracle


class AdaptiveCampaign:
    """
    Adaptive GPTFuzzer-style campaign.

    This is independent of the existing FuzzCampaign.
    """

    def __init__(self, provider):

        self.executor = FuzzExecutor(provider)

        self.ai_mutator = AIMutator()

        self.seed_pool = SeedPool()

        self.oracle = Oracle()

    def run(self, seed_prompt, max_tests):

        print("=" * 60)
        print("ADAPTIVE CAMPAIGN STARTED")
        print("=" * 60)

        # Add the initial human-written prompt
        self.seed_pool.add_prompt(
            prompt=seed_prompt,
            generation=0,
            operator="Original"
        )

        results = []

        # ------------------------------------------
        # Adaptive Fuzzing Loop
        # ------------------------------------------

        for iteration in range(max_tests):

            print()
            print("=" * 60)
            print(f"Iteration {iteration + 1}")
            print("=" * 60)

            # Select one seed from the pool

            seed = self.seed_pool.get_best_or_random()

            if seed is None:

                print("Seed Pool is empty.")

                break

            print()

            print("Selected Seed")

            print("-" * 40)

            print(seed.prompt)

            print()

            print("Generation :", seed.generation)

            print("Score      :", seed.score)

            print("Operator   :", seed.operator)
# ------------------------------------------
# Generate ONE mutation
# ------------------------------------------

            print()
            print("Generating Mutation...")
            print()

            attack = self.ai_mutator.generate(
                seed.prompt,
                count=1 )

            if not attack:
                print("Mutation generation failed.")
                continue

            attack = attack[0]
            print("Mutation Generated")
            print("-" * 40)
            print("Category :", attack["category"])
            print()
            print("Prompt")
            print(attack["prompt"])

# ------------------------------------------
# Execute attack
# ------------------------------------------

            print()
            print("Executing Attack...")
            print()

            response = self.executor.run_prompt(
                attack["prompt"]
            )

            response_text = response["response"]

            print("Target Response")
            print("-" * 40)
            print(response_text)

            # ------------------------------------------
# Oracle Evaluation
# ------------------------------------------

            oracle_result = self.oracle.evaluate(response_text)

            print()
            print("Oracle Result")
            print("-" * 40)

            print("Success :", oracle_result["success"])
            print("Score   :", oracle_result["score"])

            # ------------------------------------------
# Successful attack?
# ------------------------------------------

            if oracle_result["success"]:

                print()
                print("Adding successful mutation to Seed Pool...")

                self.seed_pool.add_prompt(

                    prompt=attack["prompt"],

                    parent=seed,

                    score=oracle_result["score"],

                    generation=seed.generation + 1,

                    operator=attack["category"]

                )

                print("Seed Pool Size :", self.seed_pool.size())

            else:

                print()

                print("Mutation discarded.")
        return results