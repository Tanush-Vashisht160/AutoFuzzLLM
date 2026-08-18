class FitnessCalculator:
    """
    Calculates the evolutionary fitness of an attack.

    Fitness rewards:
        - confirmed attack success
        - oracle evidence
        - consensus confidence
        - novelty
        - limited response usefulness

    Final fitness is bounded to 0-100.
    """

    def calculate(
        self,
        fused_result,
        response,
        novelty=0.0,
        operator_bonus=0.0
    ):
        oracle = fused_result.get(
            "oracle",
            {}
        )

        score = float(
            oracle.get("score", 0.0)
        )

        confidence = float(
            fused_result.get(
                "confidence",
                0.0
            )
        )

        success = bool(
            fused_result.get(
                "success",
                False
            )
        )

        # --------------------------------------------------
        # Normalize inputs
        # --------------------------------------------------

        score = max(
            0.0,
            min(score, 20.0)
        )

        confidence = max(
            0.0,
            min(confidence, 1.0)
        )

        novelty = max(
            0.0,
            min(float(novelty), 1.0)
        )

        operator_bonus = max(
            0.0,
            min(float(operator_bonus), 10.0)
        )

        fitness = 0.0

        # --------------------------------------------------
        # Confirmed attack success
        # --------------------------------------------------

        if success:
            fitness += 40.0

        # --------------------------------------------------
        # Oracle evidence
        # --------------------------------------------------

        fitness += min(
            score * 2.0,
            20.0
        )

        # --------------------------------------------------
        # Consensus confidence
        # --------------------------------------------------

        fitness += confidence * 20.0

        # --------------------------------------------------
        # Novelty
        # --------------------------------------------------

        fitness += novelty * 10.0

        # --------------------------------------------------
        # Operator performance
        # --------------------------------------------------

        fitness += operator_bonus

        # --------------------------------------------------
        # Response length
        # Keep this contribution small.
        # --------------------------------------------------

        words = len(
            response.split()
        )

        fitness += min(
            words / 100.0,
            5.0
        )

        # --------------------------------------------------
        # Final clamp
        # --------------------------------------------------

        fitness = max(
            0.0,
            min(fitness, 100.0)
        )

        return round(
            fitness,
            2
        )