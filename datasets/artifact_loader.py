import json
from pathlib import Path


class ArtifactLoader:

    def __init__(self, dataset_path="datasets/attack-artifacts"):
        self.dataset_path = Path(dataset_path)

    def load(self):

        seeds = []

        # Search every JSON file
        for json_file in self.dataset_path.rglob("*.json"):

            # Skip dummy test dataset
            if "test-artifact" in json_file.parts:
                continue

            # Ignore metadata files
            if json_file.name in (
                "attack-info.json",
                "evaluation.json",
                "submission.json",
            ):
                continue

            try:
                with open(json_file, "r", encoding="utf-8") as f:
                    data = json.load(f)

            except Exception as e:
                print(f"Error reading {json_file}: {e}")
                continue

            # Skip invalid files
            if "jailbreaks" not in data:
                continue

            for sample in data["jailbreaks"]:

                # Ignore empty prompts
                if sample.get("prompt") is None:
                    continue

                seeds.append({

                    "attack_method": json_file.parents[1].name,

                    "attack_type": json_file.parent.name,

                    "model": json_file.stem,

                    "category": sample.get("category"),

                    "behavior": sample.get("behavior"),

                    "goal": sample.get("goal"),

                    "prompt": sample.get("prompt"),

                    "expected_response": sample.get("response"),

                    "expected_jailbreak": sample.get("jailbroken"),

                    "queries": sample.get("number_of_queries")

                })

        return seeds