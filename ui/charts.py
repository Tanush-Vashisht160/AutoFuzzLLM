import streamlit as st
import plotly.express as px


def show_campaign_charts(df):

    if df.empty:
        st.info("No campaign data available.")
        return

    ##########################################################
    # CHART 1
    ##########################################################

    st.subheader("📊 Final Severity Distribution")

    severity_df = (
        df.groupby(["Provider", "Severity"])
        .size()
        .reset_index(name="Count")
    )

    fig1 = px.bar(
        severity_df,
        x="Provider",
        y="Count",
        color="Severity",
        barmode="group",
        text="Count",
        title="Final Verdicts per Model"
    )

    fig1.update_layout(
        xaxis_title="Model",
        yaxis_title="Number of Tests"
    )

    st.plotly_chart(fig1, use_container_width=True)

    ##########################################################
    # Dynamic Summary 1
    ##########################################################

    total_tests = len(df)

    safe = (df["Severity"] == "Safe").sum()
    warning = (df["Severity"] == "Warning").sum()
    critical = (df["Severity"] == "Critical").sum()

    critical_provider = (
        severity_df[
            severity_df["Severity"] == "Critical"
        ]
    )

    if not critical_provider.empty:

        row = critical_provider.loc[
            critical_provider["Count"].idxmax()
        ]

        highest_model = row["Provider"]
        highest_count = int(row["Count"])

        extra = (
            f"The highest number of Critical responses "
            f"was produced by **{highest_model}** "
            f"({highest_count})."
        )

    else:

        extra = "No Critical responses were observed."

    st.success(
        f"""
### 📝 Key Findings

• Total Tests: **{total_tests}**

• Safe Responses: **{safe}**

• Warning Responses: **{warning}**

• Critical Responses: **{critical}**

• {extra}
"""
    )

    st.divider()

    ##########################################################
    # CHART 2
    ##########################################################

    st.subheader("📊 Attack Category Distribution")

    attack_df = (
        df.groupby(["Attack", "Provider"])
        .size()
        .reset_index(name="Count")
    )

    fig2 = px.bar(
        attack_df,
        x="Attack",
        y="Count",
        color="Provider",
        barmode="group",
        text="Count",
        title="Attack Categories Triggered"
    )

    fig2.update_layout(
        xaxis_title="Attack Category",
        yaxis_title="Occurrences"
    )

    st.plotly_chart(fig2, use_container_width=True)

    ##########################################################
    # Dynamic Summary 2
    ##########################################################

    attack_total = (
        df.groupby("Attack")
        .size()
        .reset_index(name="Count")
    )

    top_attack = attack_total.loc[
        attack_total["Count"].idxmax()
    ]

    weakest_attack = top_attack["Attack"]
    weakest_count = int(top_attack["Count"])

    least_attack = attack_total.loc[
        attack_total["Count"].idxmin()
    ]

    least_name = least_attack["Attack"]
    least_count = int(least_attack["Count"])

    st.success(
        f"""
### 📝 Key Findings

• **{weakest_attack}** was the most frequently observed attack category with **{weakest_count}** tests.

• **{least_name}** appeared the least with **{least_count}** tests.

• A total of **{len(attack_total)}** attack categories were exercised during this campaign.

• The graph shows how attack attempts were distributed across the selected LLM providers.
"""
    )