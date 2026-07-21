import json
import yaml
from pathlib import Path


class ArtifactLoader:

    def __init__(self, dataset_name):

        if dataset_name == "Benchmark Dataset 1":
            self.dataset_path = Path("datasets/attack-artifacts")
            self.dataset_type = "json"

        elif dataset_name == "Benchmark Dataset 2":
            self.dataset_path = Path("datasets/benchmark_dataset_2")
            self.dataset_type = "yaml"

        else:
            raise ValueError(f"Unknown dataset: {dataset_name}")

    def load(self):

        if self.dataset_type == "json":
            return self._load_attack_artifacts()

        return self._load_benchmark_dataset_2()

    #####################################################
    # Dataset 1
    #####################################################

    def _load_attack_artifacts(self):

        seeds = []

        print(self.dataset_path)

        for json_file in self.dataset_path.rglob("*.json"):

            if "test-artifact" in json_file.parts:
                continue

            if json_file.name in (
                "attack-info.json",
                "evaluation.json",
                "submission.json",
            ):
                continue

            try:
                with open(json_file, "r", encoding="utf-8") as f:
                    data = json.load(f)

            except Exception:
                continue

            if "jailbreaks" not in data:
                continue

            for sample in data["jailbreaks"]:

                if sample.get("prompt") is None:
                    continue

                seeds.append({
                    "attack_method": json_file.parents[1].name,
                    "attack_type": json_file.parent.name,
                    "model": json_file.stem,
                    "category": sample.get("category", "Attack"),
                    "behavior": sample.get("behavior"),
                    "goal": sample.get("goal"),
                    "prompt": sample.get("prompt"),
                    "expected_response": sample.get("response"),
                    "expected_jailbreak": sample.get("jailbroken"),
                    "queries": sample.get("number_of_queries")
                })

        print(f"Loaded {len(seeds)} prompts from Benchmark Dataset 1")

        return seeds

    #####################################################
    # Dataset 2
    #####################################################

    def _load_benchmark_dataset_2(self):

        seeds = []

        for yaml_file in self.dataset_path.rglob("*.yaml"):

            try:
                with open(yaml_file, "r", encoding="utf-8") as f:
                    data = yaml.safe_load(f)

            except Exception as e:
                print(f"Error reading {yaml_file}: {e}")
                continue

            if not isinstance(data, dict):
                continue

            prompt = data.get("prompt")

            if not prompt:
                continue

            seeds.append({

                "attack_method": data.get("title", yaml_file.stem),

                "attack_type": "Jailbreak",

                "model": "Benchmark Dataset 2",

                "category": "Jailbreak",

                "behavior": "",

                "goal": "",

                "prompt": prompt,

                "expected_response": "",

                "expected_jailbreak": True,

                "queries": 1

            })

        print(f"Loaded {len(seeds)} prompts from Benchmark Dataset 2")

        return seeds