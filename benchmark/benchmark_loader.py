import json
import csv
from pathlib import Path


class BenchmarkLoader:

    def load_json(self, path):

        with open(path, encoding="utf8") as f:
            return json.load(f)

    def load_csv(self, path):

        rows = []

        with open(path, newline="", encoding="utf8") as f:

            reader = csv.DictReader(f)

            for row in reader:
                rows.append(row)

        return rows

    def load(self, path):

        extension = Path(path).suffix.lower()

        if extension == ".json":
            return self.load_json(path)

        if extension == ".csv":
            return self.load_csv(path)

        raise Exception("Unsupported dataset")