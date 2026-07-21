import streamlit as st
import plotly.express as px


def show_lvi_dashboard(df):

    if df.empty:
        return

    st.subheader("🛡 LLM Vulnerability Index Dashboard")

    #######################################################
    # Histogram
    #######################################################

    fig = px.histogram(
        df,
        x="LVI",
        nbins=20,
        title="LVI Distribution"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    #######################################################
    # Provider Average
    #######################################################

    provider = (
        df.groupby("Provider")["LVI"]
        .mean()
        .reset_index()
    )

    fig = px.bar(
        provider,
        x="Provider",
        y="LVI",
        title="Average LVI by Provider"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    #######################################################
    # LVI Levels
    #######################################################

    level = (
        df.groupby("LVI Level")
        .size()
        .reset_index(name="Count")
    )

    fig = px.pie(
        level,
        names="LVI Level",
        values="Count",
        title="LVI Level Distribution"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    #######################################################
    # Top 10 Dangerous
    #######################################################

    st.subheader("🔥 Top 10 Most Dangerous Prompts")

    st.dataframe(

        df.sort_values(
            "LVI",
            ascending=False
        )[

            [
                "Provider",
                "Attack",
                "LVI",
                "LVI Level",
                "Prompt"
            ]

        ].head(10),

        use_container_width=True

    )