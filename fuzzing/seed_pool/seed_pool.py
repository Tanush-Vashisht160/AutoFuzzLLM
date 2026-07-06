import random

from fuzzing.seed_pool.seed import Seed


class SeedPool:
    """
    Stores every prompt (seed) discovered during fuzzing.

    New successful mutations are added back into the pool,
    allowing future mutations to evolve from them.
    """

    def __init__(self):

        self.seeds = []

    # -------------------------------------------------
    # Add Existing Seed Object
    # -------------------------------------------------

    def add_seed(self, seed: Seed):

        self.seeds.append(seed)

    # -------------------------------------------------
    # Create New Seed
    # -------------------------------------------------

    def add_prompt(
        self,
        prompt,
        parent=None,
        score=0,
        generation=0,
        operator="Original"
    ):

        seed = Seed(
            prompt=prompt,
            parent=parent,
            score=score,
            generation=generation,
            operator=operator
        )

        self.seeds.append(seed)

        return seed

    # -------------------------------------------------
    # Random Selection
    # -------------------------------------------------

    def get_random_seed(self):

        if not self.seeds:
            return None

        return random.choice(self.seeds)

    # -------------------------------------------------
    # Best Seed
    # -------------------------------------------------

    def get_best_seed(self):

        if not self.seeds:
            return None

        return max(
            self.seeds,
            key=lambda seed: seed.score
        )

    # -------------------------------------------------
    # Update Seed Score
    # -------------------------------------------------

    def update_score(self, seed, score):

        seed.score = score

    # -------------------------------------------------
    # Remove Seed
    # -------------------------------------------------

    def remove_seed(self, seed):

        if seed in self.seeds:
            self.seeds.remove(seed)

    # -------------------------------------------------
    # Utility Functions
    # -------------------------------------------------

    def size(self):

        return len(self.seeds)

    def get_all(self):

        return self.seeds

    def clear(self):

        self.seeds.clear()

    # -------------------------------------------------
    # Score-Based Selection
    # -------------------------------------------------

    def get_best_or_random(self, explore_rate=0.30):
        """
        Hybrid selection.

        70% -> Best seed

        30% -> Random seed
        """

        if not self.seeds:
            return None

        if random.random() < explore_rate:

            print("Selection Strategy : Random Exploration")

            return self.get_random_seed()

        print("Selection Strategy : Best Seed")

        return self.get_best_seed()