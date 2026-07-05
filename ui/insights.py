import streamlit as st

def render_insights_and_verdicts(df, comparison, attack_summary):
    st.markdown("---")
    st.header("🧠 AI Security Insights")

    if len(comparison) == 1:
        model = comparison.iloc[0]
        st.info(
            f"""
### Single Model Assessment

Only **{model['Provider']}** was tested. Cross-model comparison is unavailable.

Average Risk Score: **{model['Average_Score']:.1f}**
"""
        )
    else:
        best = comparison.sort_values("Average_Score").iloc[0]
        worst = comparison.sort_values("Average_Score", ascending=False).iloc[0]
        difference = worst["Average_Score"] - best["Average_Score"]

        st.success(
            f"""
🏆 Lowest Risk Model

**{best['Provider']}**

Average Risk: {best['Average_Score']:.1f}
"""
        )

        st.error(
            f"""
⚠️ Highest Risk Model

**{worst['Provider']}**

Average Risk: {worst['Average_Score']:.1f}
"""
        )

        st.write(f"The highest-risk model scored **{difference:.1f}** points above the safest model.")

    # Attack Statistics Summaries
    if attack_summary:
        most_attack = max(attack_summary, key=attack_summary.get)
        st.info(f"🎯 Most Tested Attack Category: **{most_attack}**")

    if not df.empty and "OWASP" in df.columns:
        most_owasp = df["OWASP"].mode()[0]
        st.info(f"🛡️ Most Observed OWASP Weakness: **{most_owasp}**")


def render_security_recommendations(df):
    st.markdown("---")
    st.header("📋 Security Recommendations")

    critical_count = len(df[df["Severity"] == "Critical"])
    medium_count = len(df[df["Severity"] == "Medium"])
    low_count = len(df[df["Severity"] == "Low"])

    if critical_count >= 10:
        st.error(
            """
### Immediate Action Required

• Strengthen prompt filtering
• Improve jailbreak detection
• Add output moderation
• Review system prompt protection
• Perform additional fuzz testing
"""
        )
    elif critical_count > 0:
        st.warning(
            """
### Moderate Risk Detected

• Improve prompt validation
• Increase refusal behaviour
• Strengthen system prompt isolation
• Monitor future attacks
"""
        )
    elif medium_count > 0:
        st.info(
            """
### Minor Weaknesses Found

• Improve validation rules
• Expand attack dataset
• Continue continuous fuzz testing
"""
            )
    else:
        st.success(
            """
### Strong Security Posture

No successful attacks detected. Current safeguards appear effective. Continue periodic security testing.
"""
        )


def render_final_verdict(comparison):
    st.markdown("---")
    st.header("🏁 Final Security Verdict")

    if len(comparison) == 1:
        model = comparison.iloc[0]
        st.info(
            f"""
Only one model was tested.

**Model:** {model['Provider']}
**Average Risk Score:** {model['Average_Score']:.1f}

*Run multiple models simultaneously to unlock comparative security profiling.*
"""
        )
    else:
        best = comparison.sort_values("Average_Score").iloc[0]
        worst = comparison.sort_values("Average_Score", ascending=False).iloc[0]

        st.success(
            f"""
🏆 **Best Performing Model**

{best['Provider']}

*Average Risk Score:* {best['Average_Score']:.1f}
"""
        )

        st.error(
            f"""
⚠️ **Highest Risk Model**

{worst['Provider']}

*Average Risk Score:* {worst['Average_Score']:.1f}
"""
        )