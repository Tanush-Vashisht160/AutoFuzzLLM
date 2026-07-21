import json

from llm.llm_router import LLMRouter


class GraphExplainer:

    @staticmethod
    def explain(
        chart_name,
        dataframe,
        provider="Groq"
    ):

        if dataframe.empty:
            return "No data available."

        llm = LLMRouter(provider)

        data = dataframe.to_dict(
            orient="records"
        )

        # Select specialized analysis instructions based on the chart type
        if chart_name == "Radar Chart":
            specific_instructions = (
                "Compare the security robustness of the models. "
                "Explain strengths and weaknesses. Discuss trade-offs."
            )
        elif chart_name == "Bubble Plot":
            specific_instructions = (
                "Explain the relationship between response time, risk score, and response length. "
                "Mention any clustering or outliers."
            )
        elif chart_name == "Attack Success Matrix":
            specific_instructions = (
                "Identify which attack categories are most successful against which models. "
                "Explain trends and defensive implications."
            )
        elif chart_name == "Final Severity Distribution":
            specific_instructions = (
                "Describe the distribution of Safe, Warning, High, and Critical responses. "
                "Interpret what this says about the tested model(s)."
            )
        elif chart_name == "Attack Category Distribution":
            specific_instructions = (
                "Explain which attack types dominate. "
                "Discuss what this reveals about the mutation strategy."
            )
        elif chart_name == "Evolution Graph":
            specific_instructions = (
                "Describe how prompts evolved across generations. "
                "Highlight successful mutation operators and convergence."
            )
        else:
            specific_instructions = "Explain the visualization."

        # Re-engineered core prompt with explicit formatting guardrails
        prompt = f"""You are an AI cybersecurity researcher analyzing telemetry from an LLM fuzzing framework.

Chart Name: {chart_name}

Chart Data:
{json.dumps(data, indent=2)}

Task:
Analyze the data above and provide a comprehensive chart explanation.

Your analysis must address these four areas:
1. What this graph shows.
2. Important observations ({specific_instructions}).
3. Security implications.
4. Overall conclusion.

Formatting Constraints:
- Write professionally and objectively.
- Use continuous paragraph prose only. DO NOT use bullet points, numbered lists, or markdown lists.
- Strict length constraint: Maximum 180 words. Go straight to the analysis; do not include conversational introductions or transitions."""

        return llm.generate(prompt)