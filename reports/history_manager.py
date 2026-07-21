import json
import os
from datetime import datetime

HISTORY_DIR = "reports/history"

os.makedirs(HISTORY_DIR, exist_ok=True)


class CampaignHistoryManager:

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

        with open(path, "w", encoding="utf-8") as file:

            json.dump(
                data,
                file,
                indent=4
            )

        return path

    @staticmethod
    def load(path):

        with open(path, encoding="utf-8") as file:

            return json.load(file)