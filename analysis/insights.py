class InsightsEngine:

    def generate(self, comparison, df):

        # ---------------------------------------------------------
        # Protect against empty comparison data
        # ---------------------------------------------------------

        if comparison is None or comparison.empty:
            return ["No model comparison data available."]

        insights = []

        # ---------------------------------------------------------
        # Safest model
        # ---------------------------------------------------------

        safest = comparison.sort_values(
            "Average_Score"
        ).iloc[0]

        insights.append(
            f"🏆 Safest model: {safest['Provider']} "
            f"(Average Risk Score: {safest['Average_Score']:.1f})"
        )

        # ---------------------------------------------------------
        # Highest risk model
        # ---------------------------------------------------------

        riskiest = comparison.sort_values(
            "Average_Score",
            ascending=False
        ).iloc[0]

        insights.append(
            f"⚠ Highest risk model: {riskiest['Provider']}"
        )

        # ---------------------------------------------------------
        # Most common attack category
        # ---------------------------------------------------------

        if not df.empty and "Category" in df.columns:

            attack = df["Category"].value_counts().idxmax()

            insights.append(
                f"🎯 Most tested attack category: {attack}"
            )

        # ---------------------------------------------------------
        # Most common OWASP weakness
        # ---------------------------------------------------------

        if not df.empty and "OWASP" in df.columns:

            owasp = df["OWASP"].value_counts().idxmax()

            insights.append(
                f"🛡 Most observed OWASP weakness: {owasp}"
            )

        return insights