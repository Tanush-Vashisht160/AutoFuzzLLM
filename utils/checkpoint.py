import json
import os

CHECKPOINT_DIR = "checkpoints"

os.makedirs(CHECKPOINT_DIR, exist_ok=True)


class CampaignCheckpoint:

    @staticmethod
    def save(filename, data):

        path = os.path.join(
            CHECKPOINT_DIR,
            filename
        )

        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)

    @staticmethod
    def load(filename):

        path = os.path.join(
            CHECKPOINT_DIR,
            filename
        )

        with open(path, encoding="utf-8") as f:
            return json.load(f)

    @staticmethod
    def list_checkpoints():

        files = []

        for file in os.listdir(CHECKPOINT_DIR):

            if file.endswith(".json"):

                files.append(file)

        files.sort(reverse=True)

        return files
    
    @staticmethod
    def delete(filename):

        path = os.path.join(
            CHECKPOINT_DIR,
            filename
        )

        if os.path.exists(path):
            os.remove(path)