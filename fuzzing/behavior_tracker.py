import hashlib


class BehaviorTracker:

    def __init__(self):

        self.behaviors = set()

    def is_new_behavior(self, oracle_result):

        signature = (

            oracle_result["success"],
            oracle_result["refused"],
            oracle_result["attack_category"],
            tuple(sorted(oracle_result["matched_keywords"]))

        )

        if signature in self.behaviors:
            return False

        self.behaviors.add(signature)

        return True

    def total_behaviors(self):

        return len(self.behaviors)