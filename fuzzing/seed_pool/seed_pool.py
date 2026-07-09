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
        self.max_pool_size = 100

    # -------------------------------------------------
    # Add Existing Seed Object
    # -------------------------------------------------

    def add_seed(self, seed: Seed):

        self.seeds.append(seed)
        self.prune_pool()
    # -------------------------------------------------
    # Create New Seed (Updated with adaptive fitness parameters)
    # -------------------------------------------------

    def add_prompt(
        self,
        prompt,
        parent=None,
        score=0,
        fitness=0,
        confidence=0,
        success=False,
        attack_category="Unknown",
        generation=0,
        operator="Original"
    ):

        seed = Seed(
            prompt=prompt,
            parent=parent,
            score=score,
            fitness=fitness,
            confidence=confidence,
            success=success,
            attack_category=attack_category,
            generation=generation,
            operator=operator
        )

        self.seeds.append(seed)
        self.prune_pool()

        return seed

    # -------------------------------------------------
    # Random Selection
    # -------------------------------------------------

    def get_random_seed(self):

        if not self.seeds:
            return None

        return random.choice(self.seeds)

    # -------------------------------------------------
    # Best Seed (Updated to select by Fitness)
    # -------------------------------------------------

    def get_best_seed(self):

        if not self.seeds:
            return None

        return max(
            self.seeds,
            key=lambda seed: seed.fitness
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

    def prune_pool(self):
    #Keep only the highest-fitness seeds

        if len(self.seeds) <= self.max_pool_size:
            return

        self.seeds.sort(
            key=lambda seed: seed.fitness,
            reverse=True
        )

        removed = len(self.seeds) - self.max_pool_size

        self.seeds = self.seeds[:self.max_pool_size]

        print(f"SeedPool Pruned : Removed {removed} weak seeds")
    # -------------------------------------------------
    # Score/Fitness-Based Selection
    # -------------------------------------------------

    def get_best_or_random(self, explore_rate=0.30):
        """
        Hybrid selection.

        70% -> Best seed (highest fitness)

        30% -> Random seed
        """

        if not self.seeds:
            return None

        if random.random() < explore_rate:

            print("Selection Strategy : Random Exploration")

            return self.get_random_seed()

        print("Selection Strategy : Best Seed")

        return self.get_best_seed()
    

    def get_weighted_seed(self):

        if not self.seeds:
            return None

        total = sum(
            max(seed.fitness, 1)
            for seed in self.seeds
        )

        pick = random.uniform(0, total)

        current = 0

        for seed in self.seeds:

            current += max(seed.fitness, 1)

            if current >= pick:

                print(
                    f"Selection Strategy : Weighted ({seed.operator})"
                )

                return seed

        return self.seeds[-1]