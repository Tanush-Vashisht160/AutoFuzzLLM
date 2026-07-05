class InsightsEngine:

    def generate(self, comparison, df):

        insights = []

        # Safest model
        safest = comparison.sort_values("Average_Score").iloc[0]

        insights.append(
            f"🏆 Safest model: {safest['Provider']} "
            f"(Average Risk Score: {safest['Average_Score']:.1f})"
        )

        # Highest risk model
        riskiest = comparison.sort_values(
            "Average_Score",
            ascending=False
        ).iloc[0]

        insights.append(
            f"⚠ Highest risk model: {riskiest['Provider']}"
        )

        # Most common attack
        attack = (
            df["Category"]
            .value_counts()
            .idxmax()
        )

        insights.append(
            f"🎯 Most tested attack category: {attack}"
        )

        # Most common OWASP
        owasp = (
            df["OWASP"]
            .value_counts()
            .idxmax()
        )

        insights.append(
            f"🛡 Most observed OWASP weakness: {owasp}"
        )

        return insights