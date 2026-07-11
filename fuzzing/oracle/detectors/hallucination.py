class HallucinationDetector:

    def detect(self, text):

        lower = text.lower()

        hallucination = (
            "i made that up" in lower
            or "fictional" in lower
            or "cannot verify" in lower
            or "not based on real information" in lower
        )

        return {
            "success": hallucination,
            "keywords": [],
            "score": 1 if hallucination else 0
        }