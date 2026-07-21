from graphviz import Digraph
import streamlit as st
from analysis.graph_explainer import GraphExplainer
import pandas as pd
def show_graph(seed_pool):

    dot = Digraph("Evolution")

    dot.attr(rankdir="TB")

    for seed in seed_pool.get_all():

        node_id = str(id(seed))

        label = (
            f"{seed.operator}\n"
            f"Generation : {seed.generation}\n"
            f"Fitness : {seed.fitness}\n"
            f"V:{seed.visits}\n"
            f"R:{seed.reward:.1f}"
        )

        dot.node(
            node_id,
            label,
            shape="box",
            style="rounded"
        )

        if seed.parent:

            dot.edge(
                str(id(seed.parent)),
                node_id
            )

    st.subheader("🧬 Evolution Graph")

    st.graphviz_chart(dot)

    seeds = seed_pool.get_all()

    graph_df = pd.DataFrame({
        "Operator": [s.operator for s in seeds],
        "Generation": [s.generation for s in seeds],
        "Fitness": [s.fitness for s in seeds],
    })
    st.markdown("### 🧠 AI Interpretation")

    st.info(

        GraphExplainer.explain(

            "Evolution Graph",

            graph_df

        )

    )