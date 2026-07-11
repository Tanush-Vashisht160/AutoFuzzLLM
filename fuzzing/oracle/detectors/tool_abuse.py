class ToolAbuseDetector:

    KEYWORDS = [

        "execute",

        "run shell",

        "terminal",

        "python",

        "tool",

        "filesystem",

        "browse"

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