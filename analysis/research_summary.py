import json

from llm.llm_router import LLMRouter


class ResearchSummaryGenerator:

    @staticmethod
    def generate(comparison):

        if comparison.empty:
            return "No benchmark results available."

        data = comparison.to_dict(
            orient="records"
        )

        prompt = f"""
You are an AI security researcher.

Analyze these benchmark results.

{json.dumps(data, indent=2)}

Write a research paper style Results and Discussion section.

Include:

1. Best security model
2. Fastest model
3. Which model was more vulnerable
4. Performance trade-offs
5. Final conclusion

Do NOT use bullet points.

Use academic writing.

Maximum 220 words.
"""

        llm = LLMRouter("Groq")

        try:

            return llm.generate(prompt)

        except Exception:

            return "Unable to generate AI summary."