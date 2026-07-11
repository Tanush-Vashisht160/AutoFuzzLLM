class NoveltySearch:

    def score(self, prompt, population):

        if not population:
            return 100

        words = set(prompt.lower().split())

        similarities = []

        for p in population:

            other = set(p.lower().split())

            intersection = len(words & other)

            union = len(words | other)

            if union == 0:
                similarity = 1
            else:
                similarity = intersection / union

            similarities.append(similarity)

        avg_similarity = sum(similarities) / len(similarities)

        novelty = 100 * (1 - avg_similarity)

        return round(novelty, 2)