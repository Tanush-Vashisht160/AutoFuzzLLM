from benchmark.benchmark_runner import BenchmarkRunner
from benchmark.benchmark_metrics import BenchmarkMetrics

runner = BenchmarkRunner(
    provider="Phi3 Mini"
)

results = runner.run(

    dataset_path="datasets/test.json",

    max_tests=2
)

metrics = BenchmarkMetrics()

summary = metrics.summarize(results)

print()

print("=" * 60)
print("BENCHMARK SUMMARY")
print("=" * 60)

for key, value in summary.items():

    print(key, ":", value)