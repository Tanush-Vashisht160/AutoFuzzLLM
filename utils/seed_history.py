import json
import glob

HISTORY_FOLDER = "reports/history"


class SeedHistory:

    @staticmethod
    def get_best_prompts(
        limit=20,
        minimum_fitness=60
    ):
        """
        Load the highest-fitness prompts
        from previous campaigns.
        """

        prompts = []

        files = sorted(
            glob.glob(f"{HISTORY_FOLDER}/*.json"),
            reverse=True
        )

        for file in files:

            with open(file, encoding="utf-8") as f:

                report = json.load(f)

            for result in report.get("results", []):

                fitness = result.get("fitness", 0)

                if fitness >= minimum_fitness:

                    prompts.append(result)

        prompts.sort(
            key=lambda x: x["fitness"],
            reverse=True
        )

        return prompts[:limit]