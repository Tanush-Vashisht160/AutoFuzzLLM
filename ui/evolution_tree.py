import streamlit as st

def build_tree(seed, level=0):

    prefix = "    " * level + "├── "

    node_text = (
        f"{prefix}"
        f"**{seed.operator}**  \n"
        f"Generation : {seed.generation}  \n"
        f"Fitness : {seed.fitness}  \n"
        f"Visits : {seed.visits}  \n"
        f"Reward : {seed.reward:.2f}"
    )

    st.markdown(node_text)

    for child in seed.children:
        build_tree(child, level + 1)


def show_evolution_tree(seed_pool):

    st.subheader("🌳 Evolution Tree")

    roots = [
        seed
        for seed in seed_pool.get_all()
        if seed.parent is None
    ]

    for root in roots:
        build_tree(root)

def show_evolution_tree(seed_pool):

    st.subheader("🌳 Evolution Tree")

    roots = [
        seed
        for seed in seed_pool.get_all()
        if seed.parent is None
    ]

    for root in roots:
        build_tree(root)