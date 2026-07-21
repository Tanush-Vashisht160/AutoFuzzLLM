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
        self.max_pool_size = 1000

    # -------------------------------------------------
    # Pythonic Container Protocols
    # -------------------------------------------------

    def __iter__(self):
        """Allows direct iteration: `for seed in seed_pool:`"""
        return iter(self.seeds)

    def __len__(self):
        """Allows direct length tracking: `len(seed_pool)`"""
        return len(self.seeds)

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
        operator="Original",
        attack_method=None,
        behavior=None,
        goal=None,
        model=None,
        expected_response=None,
        expected_jailbreak=None
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
            operator=operator,
            attack_method=attack_method,
            behavior=behavior,
            goal=goal,
            model=model,
            expected_response=expected_response,
            expected_jailbreak=expected_jailbreak
        )

        if parent is not None:
            parent.children.append(seed)

        self.seeds.append(seed)
        self.prune_pool()

        return seed

    # -------------------------------------------------
    # Selection Strategies
    # -------------------------------------------------

    def get_random_seed(self):
        if not self.seeds:
            return None
        return random.choice(self.seeds)

    def get_best_seed(self):
        if not self.seeds:
            return None
        return max(self.seeds, key=lambda seed: seed.fitness)

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
        """
        Selects a seed dynamically based on relative fitness weight.
        Uses random.choices for clean, performance-optimized execution.
        """
        if not self.seeds:
            return None

        weights = [max(seed.fitness, 1) for seed in self.seeds]
        chosen_seed = random.choices(self.seeds, weights=weights, k=1)[0]
        
        print(f"Selection Strategy : Weighted ({chosen_seed.operator})")
        return chosen_seed

    # -------------------------------------------------
    # Utility Functions
    # -------------------------------------------------

    def update_score(self, seed, score):
        seed.score = score

    def remove_seed(self, seed):
        if seed in self.seeds:
            self.seeds.remove(seed)

    def size(self):
        """Deprecated in favor of len(instance), kept for compatibility."""
        return len(self)

    def get_all(self):
        return self.seeds

    def clear(self):
        self.seeds.clear()

    def prune_pool(self):
        """Keep only the highest-fitness seeds"""
        if len(self.seeds) <= self.max_pool_size + 50:
            return

        self.seeds.sort(key=lambda seed: seed.fitness, reverse=True)
        self.seeds = self.seeds[:self.max_pool_size]