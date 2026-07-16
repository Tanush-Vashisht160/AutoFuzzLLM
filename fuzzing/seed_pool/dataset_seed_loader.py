from datasets.artifact_loader import ArtifactLoader


class DatasetSeedLoader:
    """
    Loads prompts from the Attack-Artifacts dataset
    and inserts them into the SeedPool.
    """

    def __init__(self):

        self.loader = ArtifactLoader()

    def load_into_seed_pool(self, seed_pool):

        prompts = self.loader.load()

        count = 0

        for item in prompts:

            seed_pool.add_prompt(

                prompt=item["prompt"],

                attack_category=item["category"],

                attack_method=item["attack_method"],

                behavior=item["behavior"],

                goal=item["goal"],

                model=item["model"],

                expected_response=item["expected_response"],

                expected_jailbreak=item["expected_jailbreak"]

            )

            count += 1

        print(f"\nLoaded {count} benchmark prompts into SeedPool.\n")