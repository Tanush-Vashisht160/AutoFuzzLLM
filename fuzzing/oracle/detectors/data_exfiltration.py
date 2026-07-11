class DataExfiltrationDetector:

    KEYWORDS = [

        "password",

        "secret",

        "api key",

        "private",

        "database",

        "confidential",

        "token"

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