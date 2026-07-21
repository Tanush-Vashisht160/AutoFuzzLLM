import json
import os
from datetime import datetime

HISTORY_DIR = "reports/history"

os.makedirs(HISTORY_DIR, exist_ok=True)


class CampaignHistory:

    @staticmethod
    def save(results, summary, config):

        filename = datetime.now().strftime(
            "campaign_%Y%m%d_%H%M%S.json"
        )

        path = os.path.join(HISTORY_DIR, filename)

        data = {
            "created": datetime.now().isoformat(),
            "config": config,
            "summary": summary,
            "results": results
        }

        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)

        return path

    @staticmethod
    def list_campaigns():

        files = []

        for file in os.listdir(HISTORY_DIR):

            if file.endswith(".json"):
                files.append(file)

        files.sort(reverse=True)

        return files

    @staticmethod
    def load(filename):

        path = os.path.join(HISTORY_DIR, filename)

        with open(path, encoding="utf-8") as f:
            return json.load(f)