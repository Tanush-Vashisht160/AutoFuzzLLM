import pandas as pd


class DashboardInsights:

    @staticmethod
    def generate(comparison_df: pd.DataFrame):

        if comparison_df.empty:
            return "No comparison data available."

        text = []

        # -----------------------------
        # Best Risk
        # -----------------------------
        best_risk = comparison_df.loc[
            comparison_df["Average_Score"].idxmin()
        ]

        text.append(
            f"• **{best_risk['Provider']}** achieved the lowest average "
            f"risk score ({best_risk['Average_Score']:.1f}), "
            f"indicating the strongest overall resistance to adversarial prompts."
        )

        # -----------------------------
        # Fastest
        # -----------------------------
        fastest = comparison_df.loc[
            comparison_df["Average_Time"].idxmin()
        ]

        text.append(
            f"• **{fastest['Provider']}** produced responses the fastest "
            f"with an average latency of "
            f"{fastest['Average_Time']:.2f} seconds."
        )

        # -----------------------------
        # Verbose
        # -----------------------------
        longest = comparison_df.loc[
            comparison_df["Average_Length"].idxmax()
        ]

        text.append(
            f"• **{longest['Provider']}** generated the longest responses "
            f"({longest['Average_Length']:.0f} words on average), "
            f"suggesting more detailed outputs."
        )

        # -----------------------------
        # Attack Success
        # -----------------------------
        if "Attack_Success_Rate" in comparison_df.columns:

            weakest = comparison_df.loc[
                comparison_df["Attack_Success_Rate"].idxmax()
            ]

            strongest = comparison_df.loc[
                comparison_df["Attack_Success_Rate"].idxmin()
            ]

            text.append(
                f"• Prompt attacks were most successful against "
                f"**{weakest['Provider']}** "
                f"({weakest['Attack_Success_Rate']:.1f}%)."
            )

            text.append(
                f"• **{strongest['Provider']}** demonstrated the highest "
                f"overall robustness with the lowest attack success rate "
                f"({strongest['Attack_Success_Rate']:.1f}%)."
            )

        # -----------------------------
        # Overall Winner
        # -----------------------------
        score = (
            comparison_df["Average_Score"].rank()
            + comparison_df["Average_Time"].rank()
            + comparison_df["Attack_Success_Rate"].rank()
        )

        winner = comparison_df.iloc[
            score.idxmin()
        ]

        text.append(
            f"\n### Overall Observation\n"
            f"Considering response quality, latency, and attack resilience, "
            f"**{winner['Provider']}** delivered the strongest overall "
            f"performance in this campaign."
        )

        return "\n\n".join(text)