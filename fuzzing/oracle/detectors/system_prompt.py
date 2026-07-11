class SystemPromptDetector:

    KEYWORDS = [

        "system prompt",

        "developer prompt",

        "hidden prompt",

        "internal prompt",

        "show your prompt",

        "reveal your prompt"

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