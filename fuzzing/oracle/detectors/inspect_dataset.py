from pathlib import Path

dataset = Path("datasets/attack-artifacts")

for file in dataset.rglob("*.json"):
    print(file)