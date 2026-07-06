from concurrent.futures import ThreadPoolExecutor
from fuzzing.mutations.operators import PromptMutator
from llm.openrouter_client import OpenRouterClient
from scorer import ResponseScorer
import json
import time
import os

class FuzzRunner:

    def __init__(self):
        self.mutator = PromptMutator()
        self.client = OpenRouterClient()
        self.scorer = ResponseScorer()

    # -----------------------------
    # RUN FUZZING PIPELINE
    # -----------------------------
    def run(self, seed_prompt, n_mutations=10):

        print("\n🚀 Starting fuzzing run...\n")

        mutations = self.mutator.generate_mutations(seed_prompt, n=n_mutations)

        results = []

        start_time = time.time()

        # PARALLEL EXECUTION (FAST ⚡)
        with ThreadPoolExecutor(max_workers=8) as executor:

            futures = []

            for m in mutations:
                futures.append(
                    executor.submit(self._execute, m)
                )

            for f in futures:
                results.append(f.result())

        end_time = time.time()

        print(f"\n✅ Fuzzing completed in {round(end_time - start_time, 2)}s")

        return results

    # -----------------------------
    # SINGLE EXECUTION UNIT
    # -----------------------------
    def _execute(self, mutation):

        prompt = mutation["mutation"]

        try:
            response = self.client.generate_response(prompt)

            score = self.scorer.score(response["response"])

            result = {
                "id": mutation["id"],
                "strategy": mutation["strategy"],
                "seed": mutation["seed"],
                "prompt": prompt,
                "response": response["response"],
                "time": response["response_time"],
                "score": score
            }

            # -------------------------
            # LOG TO FILE (IMPORTANT)
            # -------------------------
            os.makedirs("logs", exist_ok=True)

            with open("logs/fuzz_results.jsonl", "a") as f:
                f.write(json.dumps(result) + "\n")

            return result

        except Exception as e:

            return {
                "id": mutation["id"],
                "error": str(e),
                "prompt": prompt
            }


# -----------------------------
# TEST RUN
# -----------------------------
if __name__ == "__main__":

    runner = FuzzRunner()

    results = runner.run(
        seed_prompt="Explain how authentication works",
        n_mutations=8
    )

    print("\n📊 SAMPLE OUTPUT:\n")

    print(json.dumps(results[0], indent=2))
