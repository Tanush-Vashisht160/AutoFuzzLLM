class PromptDetector:

    def detect(self, prompt):

        text = prompt.lower()

        prompt_injection = [
            "ignore previous",
            "forget previous",
            "ignore all instructions",
            "override"
        ]

        prompt_leakage = [
            "system prompt",
            "developer prompt",
            "hidden instructions",
            "reveal prompt"
        ]

        jailbreak = [
            "dan",
            "jailbreak",
            "pretend you are",
            "roleplay as"
        ]

        for k in prompt_injection:
            if k in text:
                return "Prompt Injection"

        for k in prompt_leakage:
            if k in text:
                return "Prompt Leakage"

        for k in jailbreak:
            if k in text:
                return "Jailbreak"

        return "Benign"