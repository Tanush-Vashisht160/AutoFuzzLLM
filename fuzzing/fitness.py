class FitnessCalculator:
    """
    Calculates the fitness of an attack.

    Higher fitness means the mutation should be selected
    more often for future generations.
    """

    def calculate(
        self,
        fused_result,
        response,
        novelty=0,
        operator_bonus=0
    ):
        oracle = fused_result.get("oracle", {})
        score = oracle.get("score", 0)
        confidence = fused_result.get("confidence", 0)

        fitness = 0.0

        # -------------------------
        # Oracle Score
        # -------------------------
        fitness += score * 10

        # -------------------------
        # Attack Success
        # -------------------------
        if fused_result.get("success", False):
            fitness += 30

        # -------------------------
        # Confidence
        # -------------------------
        fitness += confidence * 20

        # -------------------------
        # Novelty Search Integration
        # -------------------------
        fitness += novelty * 0.5

        # -------------------------
        # Adaptive Operator Performance Bonus
        # -------------------------
        fitness += operator_bonus

        # -------------------------
        # Response Length Efficiency (Clamped)
        # -------------------------
        words = len(response.split())
        fitness += min(words / 25, 20)

        # -------------------------
        # Safety Boundary Clamp
        # -------------------------
        fitness = max(fitness, 0.0)

        return round(fitness, 2)