class InstructionOverrideDetector:

    KEYWORDS = [

        "ignore previous",

        "forget instructions",

        "override instructions",

        "new system",

        "replace previous",

        "disregard"

    ]

    def detect(self, text):

        lower = text.lower()

        matched = [

            k

            for k in self.KEYWORDS

            if k in lower

        ]

        return {

            "success": len(matched) > 0,

            "keywords": matched,

            "score": len(matched)

        }