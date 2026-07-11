class BehaviorTracker:
    """
    Tracks unique model behaviours during fuzzing.

    Supports both:
    - Oracle-only results
    - Fused Oracle + AI Judge results
    """

    def __init__(self):

        self.behaviors = set()

    def is_new_behavior(self, result):

        # --------------------------------------------
        # If ResultFusion output was passed
        # --------------------------------------------
        if "oracle" in result:

            oracle = result["oracle"]

            success = result.get("success", False)

            category = result.get("category", "Unknown")

            refused = oracle.get("refused", False)

            matched_keywords = oracle.get("matched_keywords", [])

        # --------------------------------------------
        # Oracle-only compatibility
        # --------------------------------------------
        else:

            success = result.get("success", False)

            refused = result.get("refused", False)

            category = result.get(
                "attack_category",
                result.get("category", "Unknown")
            )

            matched_keywords = result.get(
                "matched_keywords",
                []
            )

        signature = (

            success,

            refused,

            category,

            tuple(sorted(matched_keywords))

        )

        if signature in self.behaviors:

            return False

        self.behaviors.add(signature)

        return True

    def total_behaviors(self):

        return len(self.behaviors)