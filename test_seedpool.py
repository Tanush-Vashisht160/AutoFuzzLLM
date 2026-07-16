from fuzzing.seed_pool.seed_pool import SeedPool
from fuzzing.seed_pool.dataset_seed_loader import DatasetSeedLoader

pool = SeedPool()

loader = DatasetSeedLoader()

loader.load_into_seed_pool(pool)

print("Total seeds:", pool.size())

seed = pool.get_random_seed()

print()

print("Prompt:")
print(seed.prompt)

print()

print("Category:", seed.attack_category)
print("Behavior:", seed.behavior)
print("Method:", seed.attack_method)
print("Expected Jailbreak:", seed.expected_jailbreak)