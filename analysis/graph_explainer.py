import json

from llm.llm_router import LLMRouter


class GraphExplainer:

    @staticmethod
    def explain(
        chart_name,
        dataframe,
        provider="Groq"
    ):

        if dataframe is None or dataframe.empty:
            return "No data available for this chart."

        llm = LLMRouter(provider)

        # ---------------------------------------------------------
        # Keep only the columns that matter for each chart
        # ---------------------------------------------------------

        if chart_name == "Final Severity Distribution":

            columns = [
                col for col in [
                    "Provider",
                    "Severity",
                    "Count"
                ]
                if col in dataframe.columns
            ]

            data = dataframe[columns].to_dict(orient="records")

            instructions = """
Analyze the severity counts only.

State:
1. Which severity level dominates.
2. The total number of tests if it can be calculated.
3. Whether Critical or Warning results exist.
4. One short security conclusion based strictly on the data.

Do NOT claim that the model is robust merely because no attacks were observed.
"""

        elif chart_name == "Attack Category Distribution":

            columns = [
                col for col in [
                    "Attack",
                    "Provider",
                    "Count"
                ]
                if col in dataframe.columns
            ]

            data = dataframe[columns].to_dict(orient="records")

            instructions = """
Analyze the attack category counts only.

State:
1. The most frequent attack category.
2. The least frequent category if clear.
3. How many categories were tested.
4. One short observation about the distribution.

Do NOT claim that the model is vulnerable or robust unless the data directly supports that conclusion.
"""

        elif chart_name == "Evolution Graph":

            columns = [
                col for col in [
                    "Operator",
                    "Generation",
                    "Fitness",
                    "Visits",
                    "Reward"
                ]
                if col in dataframe.columns
            ]

            data = dataframe[columns].to_dict(orient="records")

            instructions = """
Analyze the evolution data only.

State:
1. The starting generation/fitness if available.
2. The highest fitness observed.
3. Which mutation/operator produced the highest fitness if available.
4. Whether fitness generally increased, decreased, or fluctuated.

Do NOT discuss vulnerabilities, attacks, or model robustness unless the supplied data directly contains evidence for it.
"""

        elif chart_name == "Radar Chart":

            data = dataframe.to_dict(orient="records")

            instructions = """
Briefly compare the models using the supplied metrics.
Mention the strongest and weakest visible dimensions.
Do not invent metrics or security conclusions.
"""

        elif chart_name == "Bubble Plot":

            data = dataframe.to_dict(orient="records")

            instructions = """
Briefly describe the relationship between response time,
risk score, and response length.
Mention only visible trends or outliers.
Do not invent explanations.
"""

        elif chart_name == "Attack Success Matrix":

            data = dataframe.to_dict(orient="records")

            instructions = """
Identify the attack categories with the highest and lowest
success values and the affected models.
Keep the explanation strictly data-based.
"""

        else:

            data = dataframe.to_dict(orient="records")

            instructions = """
Briefly describe the main pattern visible in the supplied data.
Do not make unsupported security claims.
"""

        # ---------------------------------------------------------
        # Short, strict LLM prompt
        # ---------------------------------------------------------

        prompt = f"""
You are analyzing one chart from an LLM security fuzzing dashboard.

Chart: {chart_name}

Data:
{json.dumps(data, indent=2, default=str)}

Instructions:
{instructions}

OUTPUT RULES:
- Maximum 70 words.
- Exactly ONE paragraph.
- No bullet points.
- No numbered lists.
- No headings.
- No markdown.
- No generic recommendations.
- No phrases such as "further testing is necessary".
- Do not repeat the chart title.
- Use ONLY the supplied data.
- If the data is insufficient for a claim, do not make that claim.
- Be precise and concise.
"""

        try:
            response = llm.generate(prompt)

            if isinstance(response, dict):
                response = response.get(
                    "response",
                    response.get("text", "")
                )

            response = str(response).strip()

            return response

        except Exception as e:
            return f"Unable to generate chart interpretation: {e}"