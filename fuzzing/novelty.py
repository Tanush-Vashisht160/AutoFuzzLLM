class NoveltySearch:
    """
    Calculates normalized lexical novelty.

    Returns a value between 0.0 and 1.0.

    0.0 = very similar to existing population
    1.0 = highly different from existing population
    """

    def score(self, prompt, population):

        if not population:
            return 1.0

        prompt_words = set(
            prompt.lower().split()
        )

        if not prompt_words:
            return 0.0

        similarities = []

        for p in population:

            # Skip empty population entries
            if not p:
                continue

            other_words = set(
                p.lower().split()
            )

            union = len(
                prompt_words | other_words
            )

            if union == 0:
                continue

            intersection = len(
                prompt_words & other_words
            )

            similarity = (
                intersection / union
            )

            similarities.append(similarity)

        if not similarities:
            return 1.0

        # Use the most similar existing prompt.
        # This is more useful for evolutionary fuzzing
        # than averaging the entire population.
        max_similarity = max(similarities)

        novelty = 1.0 - max_similarity

        return round(
            max(0.0, min(1.0, novelty)),
            4
        )