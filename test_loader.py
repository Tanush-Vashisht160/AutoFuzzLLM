from pathlib import Path
from benchmark.benchmark_loader import BenchmarkLoader

loader = BenchmarkLoader()

path = Path("datasets") / "test.json"

data = loader.load(path)

print(data)