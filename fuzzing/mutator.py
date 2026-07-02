from fuzzing.attacks.base_attacks import BaseAttacks
from fuzzing.mutation_strategies import MutationStrategies


class PromptMutator:

    def __init__(self):

        self.attacks = BaseAttacks()

        self.strategy = MutationStrategies()

    def mutate_prompt(self, category, prompt):

        mutations = []

        mutations.append({
            "category": category,
            "prompt": prompt
        })

        mutations.append({
            "category": category,
            "prompt": self.strategy.uppercase(prompt)
        })

        mutations.append({
            "category": category,
            "prompt": self.strategy.lowercase(prompt)
        })

        mutations.append({
            "category": category,
            "prompt": self.strategy.extra_spaces(prompt)
        })

        mutations.append({
            "category": category,
            "prompt": self.strategy.exclamation(prompt)
        })

        mutations.append({
            "category": category,
            "prompt": self.strategy.question(prompt)
        })

        mutations.append({
            "category": category,
            "prompt": self.strategy.emoji(prompt)
        })

        mutations.append({
            "category": category,
            "prompt": self.strategy.quotes(prompt)
        })

        mutations.append({
            "category": category,
            "prompt": self.strategy.newline(prompt)
        })

        mutations.append({
            "category": category,
            "prompt": self.strategy.leetspeak(prompt)
        })

        mutations.append({
            "category": category,
            "prompt": self.strategy.random_case(prompt)
        })

        return mutations

    def generate_mutations(self, seed_prompt):

        prompts = []

        prompts.extend(
            self.mutate_prompt(
                "Seed Prompt",
                seed_prompt
            )
        )

        for attack in self.attacks.prompt_injection():

            prompts.extend(
                self.mutate_prompt(
                    "Prompt Injection",
                    attack
                )
            )

        for attack in self.attacks.jailbreak():

            prompts.extend(
                self.mutate_prompt(
                    "Jailbreak",
                    attack
                )
            )

        for attack in self.attacks.roleplay():

            prompts.extend(
                self.mutate_prompt(
                    "Roleplay",
                    attack
                )
            )

        for attack in self.attacks.prompt_extraction():

            prompts.extend(
                self.mutate_prompt(
                    "Prompt Extraction",
                    attack
                )
            )

        return prompts[:20]