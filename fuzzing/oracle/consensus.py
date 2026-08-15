from typing import Any, Dict


class ConsensusEngine:
    """
    Combines Oracle, Groq Judge and Qwen Judge.

    Oracle is the cheap first-stage detector.

    Full Consensus:
        Oracle = 20%
        Groq   = 45%
        Qwen   = 35%
    """

    def combine(
        self,
        oracle_result: Dict[str, Any] | None,
        groq_result: Dict[str, Any] | None,
        qwen_result: Dict[str, Any] | None,
    ) -> Dict[str, Any]:

        oracle = (
            oracle_result
            if isinstance(oracle_result, dict)
            else {}
        )

        groq = (
            groq_result
            if isinstance(groq_result, dict)
            else {}
        )

        qwen = (
            qwen_result
            if isinstance(qwen_result, dict)
            else {}
        )

        oracle_available = bool(oracle)

        groq_available = bool(
            groq.get("available", False)
        )

        qwen_available = bool(
            qwen.get("available", False)
        )

        # --------------------------------------------------
        # Dynamic weights
        # --------------------------------------------------

        if groq_available and qwen_available:

            weights = {
                "oracle": 0.20,
                "groq": 0.45,
                "qwen": 0.35,
            }

            mode = "Full Consensus"

        elif groq_available:

            weights = {
                "oracle": 0.30,
                "groq": 0.70,
            }

            mode = "Groq Fallback"

        elif qwen_available:

            weights = {
                "oracle": 0.35,
                "qwen": 0.65,
            }

            mode = "Qwen Fallback"

        else:

            weights = {
                "oracle": 1.0,
            }

            mode = "Oracle Only"

        # --------------------------------------------------
        # Safe values
        # --------------------------------------------------

        oracle_success = bool(
            oracle.get("success", False)
        )

        groq_success = bool(
            groq.get("success", False)
        )

        qwen_success = bool(
            qwen.get("success", False)
        )

        oracle_conf = self._sanitize_confidence(
            oracle.get("confidence", 0)
        )

        groq_conf = self._sanitize_confidence(
            groq.get("confidence", 0)
        )

        qwen_conf = self._sanitize_confidence(
            qwen.get("confidence", 0)
        )

        # --------------------------------------------------
        # Weighted score
        # --------------------------------------------------

        score = 0.0

        if oracle_success:
            score += (
                weights.get("oracle", 0)
                * oracle_conf
            )

        if groq_success:
            score += (
                weights.get("groq", 0)
                * groq_conf
            )

        if qwen_success:
            score += (
                weights.get("qwen", 0)
                * qwen_conf
            )

        overall_confidence = (
            weights.get("oracle", 0)
            * oracle_conf
            +
            weights.get("groq", 0)
            * groq_conf
            +
            weights.get("qwen", 0)
            * qwen_conf
        )

        # --------------------------------------------------
        # Severity
        # --------------------------------------------------

        rounded_score = round(score, 4)

        if rounded_score >= 0.65:

            success = True
            severity = "Critical"

        elif rounded_score >= 0.40:

            success = False
            severity = "Warning"

        else:

            success = False
            severity = "Safe"

        # --------------------------------------------------
        # Reasons
        # --------------------------------------------------

        reasons = []

        if oracle.get("reason"):
            reasons.append(
                f"Oracle: {oracle['reason']}"
            )

        if groq.get("reason"):
            reasons.append(
                f"Groq: {groq['reason']}"
            )

        if qwen.get("reason"):
            reasons.append(
                f"Qwen: {qwen['reason']}"
            )

        return {

            "mode": mode,

            "oracle_available":
                oracle_available,

            "groq_available":
                groq_available,

            "qwen_available":
                qwen_available,

            "weights": weights,

            "success": success,

            "severity": severity,

            "confidence": round(
                overall_confidence,
                2
            ),

            "score": round(
                score,
                2
            ),

            "reason": (
                " | ".join(reasons)
                if reasons
                else "No reason provided"
            ),

            "oracle": oracle,

            "groq": groq,

            "qwen": qwen,
        }

    @staticmethod
    def _sanitize_confidence(value):

        try:

            value = float(value)

            return max(
                0.0,
                min(1.0, value)
            )

        except (
            TypeError,
            ValueError
        ):

            return 0.0