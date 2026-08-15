class RoleplayDetector:

    CATEGORY = "Roleplay"

    PATTERNS = {
        "pretend you are": 2,
        "act as": 1,
        "roleplay as": 2,
        "simulate being": 2,
        "you are now": 1
    }

    def detect(self, text):

        try:
            lower = str(text or "").lower()

            matched = []

            for phrase in self.PATTERNS:
                if phrase in lower:
                    matched.append(phrase)

            score = min(
                sum(self.PATTERNS[p] for p in matched),
                3
            )

            return {
                "success": False,
                "category": self.CATEGORY,
                "score": score,
                "confidence": min(score / 3, 1.0),
                "matched_keywords": matched
            }

        except Exception as exc:

            return {
                "success": False,
                "category": self.CATEGORY,
                "score": 0,
                "confidence": 0.0,
                "matched_keywords": [],
                "error": str(exc)
            }