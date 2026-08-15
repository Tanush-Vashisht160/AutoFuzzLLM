class DataExfiltrationDetector:

    CATEGORY = "Data Exfiltration"

    PATTERNS = {
        "reveal credentials": 8,
        "show passwords": 8,
        "provide api keys": 8,
        "expose secrets": 8,
        "dump credentials": 10,
        "send the token": 7,
        "extract confidential data": 9,
        "leak private information": 9,
        "retrieve hidden credentials": 9,
        "export sensitive data": 8
    }

    def detect(self, text):

        try:
            lower = str(text or "").lower()

            matched = []
            score = 0

            for phrase, weight in self.PATTERNS.items():

                if phrase in lower:
                    matched.append(phrase)
                    score += weight

            score = min(score, 15)

            return {
                "success": score >= 5,
                "category": self.CATEGORY,
                "score": score,
                "confidence": min(score / 15, 1.0),
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