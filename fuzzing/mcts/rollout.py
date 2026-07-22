import random


class MCTSRollout:
    """
    Performs lightweight simulations (rollouts)
    from a selected prompt before the expensive
    LLM execution.

    The rollout approximates future mutations
    to estimate branch quality.
    """

    def __init__(self, mutator):

        self.mutator = mutator

    def simulate(
        self,
        prompt: str,
        depth: int = 3,
    ):

        MAX_PROMPT_LENGTH = 10000

        current_prompt = str(prompt)

        history = []

        for step in range(depth):

            try:

                mutations = self.mutator.generate_mutations(
                    current_prompt,
                    n=1,
                )

                if not mutations:
                    break

                mutation = mutations[0]

                if isinstance(mutation, dict):

                    current_prompt = mutation.get(
                        "prompt",
                        mutation.get("mutation", "")
                    )

                elif isinstance(mutation, str):

                    current_prompt = mutation

                else:

                    raise TypeError(
                        f"Unsupported mutation type "
                        f"{type(mutation)}"
                    )

                current_prompt = str(current_prompt)

                if len(current_prompt) > MAX_PROMPT_LENGTH:

                    print(
                        f"⚠ Rollout prompt exceeded "
                        f"{MAX_PROMPT_LENGTH} chars "
                        f"(actual={len(current_prompt)})."
                    )

                    current_prompt = current_prompt[:MAX_PROMPT_LENGTH]

                history.append(current_prompt)

            except Exception as e:

                print(
                    f"Rollout stopped at depth "
                    f"{step+1}: {e}"
                )

                break

        return current_prompt, history