import json
from pprint import pprint

file = "datasets/attack-artifacts/PAIR/black_box/gpt-3.5-turbo-1106.json"

with open(file, "r", encoding="utf-8") as f:
    data = json.load(f)

print(type(data))
print("\nTop level keys:\n")

for k in data.keys():
    print(k)