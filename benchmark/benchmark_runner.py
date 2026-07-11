from benchmark.benchmark_loader import BenchmarkLoader
from fuzzing.campaign import FuzzCampaign


class BenchmarkRunner:

    def __init__(self, provider):

        self.loader = BenchmarkLoader()

        self.provider = provider

    def run(
        self,
        dataset_path,
        mutation_engine="AI Generated Mutations (Recommended)",
        max_tests=3
    ):

        dataset = self.loader.load(dataset_path)

        campaign = FuzzCampaign(
            provider=self.provider,
            mutation_engine=mutation_engine
        )

        all_results = []

        print("=" * 60)
        print("BENCHMARK STARTED")
        print("=" * 60)

        print("Dataset Size :", len(dataset))

        for index, sample in enumerate(dataset, start=1):

            print("\n")
            print("=" * 60)
            print(f"Benchmark Sample {index}/{len(dataset)}")
            print("=" * 60)

            prompt = sample["prompt"]

            print("Category :", sample.get("category", "Unknown"))
            print("Prompt   :", prompt)

            results = campaign.run(
                seed_prompt=prompt,
                max_tests=max_tests
            )

            all_results.extend(results)

        print("\n")
        print("=" * 60)
        print("BENCHMARK FINISHED")
        print("=" * 60)

        return all_results