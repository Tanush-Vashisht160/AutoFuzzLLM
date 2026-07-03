class OWASPMapper:

    def __init__(self):

        self.mapping = {

            "Prompt Injection":
                "LLM01 - Prompt Injection",

            "Jailbreak":
                "LLM01 - Prompt Injection",

            "Roleplay":
                "LLM01 - Prompt Injection",

            "System Prompt Leakage":
                "LLM07 - System Prompt Leakage",

            "Sensitive Data":
                "LLM02 - Sensitive Information Disclosure",

            "Data Extraction":
                "LLM02 - Sensitive Information Disclosure",

            "Code Generation":
                "LLM05 - Improper Output Handling",

            "Malware":
                "LLM05 - Improper Output Handling",

            "Phishing":
                "LLM05 - Improper Output Handling",

            "Tool Abuse":
                "LLM08 - Excessive Agency",

            "Multi-Turn":
                "LLM01 - Prompt Injection",

            "Seed Prompt":
                "LLM01 - Prompt Injection"
        }

    def get_category(self, attack):

        return self.mapping.get(attack, "Unknown")