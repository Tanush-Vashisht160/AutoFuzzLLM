import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from analysis.graph_explainer import GraphExplainer

def show_multi_model_dashboard(df):

    st.markdown("---")

    st.header("📊 Multi-Model Comparison Dashboard")

    st.info(
        """
This dashboard compares every selected LLM using
multiple security and performance metrics.
"""
    )

    comparison = (
    df.groupby("Provider")
      .agg(
          Average_Risk=("Score", "mean"),
          Average_Time=("Time (s)", "mean"),
          Critical=(
              "Severity",
              lambda x: (x == "Critical").sum()
          ),
          Warning=(
              "Severity",
              lambda x: (x == "Warning").sum()
          ),
          Success=(
              "Status",
              lambda x: (x == "Success").sum()
          ),
          Total=("Score", "count")
      )
      .reset_index()
)
    ######################################################
    # Calculate comparison metrics
    ######################################################

    comparison["Success Rate"] = (
        comparison["Success"] /
        comparison["Total"]
    ) * 100

    comparison["Warning Rate"] = (
        comparison["Warning"] /
        comparison["Total"]
    ) * 100

    comparison["Critical Rate"] = (
        comparison["Critical"] /
        comparison["Total"]
    ) * 100


    ######################################################
    # Normalize Response Time
    # Faster = Higher Score
    ######################################################

    max_time = comparison["Average_Time"].max()
    min_time = comparison["Average_Time"].min()

    if max_time == min_time:
        comparison["Time Score"] = 100
    else:
        comparison["Time Score"] = (
            (max_time - comparison["Average_Time"])
            /
            (max_time - min_time)
        ) * 100

    chart1, chart2 = st.columns(2)

    with chart1:

        st.subheader("🕸 Radar Chart")

        radar = go.Figure()

        metrics = [
            "Average_Risk",
            "Success Rate",
            "Critical Rate",
            "Warning Rate",
            "Time Score"
        ]

        labels = [
            "Risk",
            "Success",
            "Critical",
            "Warning",
            "Speed"
        ]

        for _, row in comparison.iterrows():

            values = [
                row["Average_Risk"],
                row["Success Rate"],
                row["Critical Rate"],
                row["Warning Rate"],
                row["Time Score"]
            ]

            values.append(values[0])

            radar.add_trace(
                go.Scatterpolar(
                    r=values,
                    theta=labels + [labels[0]],
                    fill="toself",
                    name=row["Provider"]
                )
            )

        radar.update_layout(

            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0,100]
                )
            ),

            showlegend=True,
            height=500
        )

        st.plotly_chart(
            radar,
            use_container_width=True
        )
        st.markdown("### 🧠 AI Interpretation")

        st.info(

            GraphExplainer.explain(

                "Radar Chart",

                comparison

            )

        )
    with chart2:

        st.subheader("🫧 Bubble Plot")

        bubble = px.scatter(

            comparison,

            x="Average_Time",

            y="Average_Risk",

            size="Critical",

            color="Provider",

            text="Provider",

            hover_data=[
                "Success",
                "Warning",
                "Critical",
                "Total"
            ]
        )

        bubble.update_traces(

            textposition="top center"
        )

        bubble.update_layout(

            xaxis_title="Average Response Time (s)",

            yaxis_title="Average Risk Score",

            height=500
        )

        st.plotly_chart(

            bubble,

            use_container_width=True
        )
        st.markdown("### 🧠 AI Interpretation")

        st.info(

            GraphExplainer.explain(

                "Bubble Plot",

                comparison

            )

        )
    st.subheader("🔥 Attack Success Matrix")

    ######################################################
    # Build Matrix
    ######################################################

    matrix = (

        df.groupby(

            [

                "Attack",

                "Provider"

            ]

        )

        .apply(

            lambda x:

            (

                x["Status"] == "Success"

            ).mean() * 100

        )

        .reset_index(

            name="Success Rate"

        )

    )

    ######################################################
    # Pivot Table
    ######################################################

    heatmap_df = matrix.pivot(

        index="Attack",

        columns="Provider",

        values="Success Rate"

    )

    ######################################################
    # Plot
    ######################################################

    heatmap = px.imshow(

        heatmap_df,

        text_auto=".0f",

        aspect="auto",

        labels=dict(

            color="Success %"

        )

    )

    heatmap.update_layout(

        height=500

    )

    st.plotly_chart(

        heatmap,

        use_container_width=True

    )
    st.markdown("### 🧠 AI Interpretation")

    st.info(

        GraphExplainer.explain(

            "Attack Success Matrix",

            comparison

        )

    )