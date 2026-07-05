import streamlit as st


def show_graph_insight(
    title,
    what,
    why,
    interpretation,
    danger,
    conclusion
):

    with st.expander(f"📖 Understanding: {title}", expanded=True):

        st.markdown("### 📌 What is this graph?")
        st.write(what)

        st.markdown("### 🎯 Why is it important?")
        st.write(why)

        st.markdown("### 📊 What does YOUR campaign show?")
        st.write(interpretation)

        st.markdown("### ⚠ What would indicate a bad result?")
        st.write(danger)

        st.markdown("### ✅ Conclusion")
        st.success(conclusion)