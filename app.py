import streamlit as st
from core_state import get_core_engines, initialize_application_state
from tabs.batch_campaign import render_batch_campaign_tab
from tabs.live_fuzzer import render_live_fuzzer_tab
from pathlib import Path

# CRITICAL: Page config must be the very first Streamlit command executed
st.set_page_config(page_title="AutoFuzzLLM", page_icon="🛡️", layout="wide")
css_path = Path(__file__).parent / "ui" / "styles.css"

with open(css_path, encoding="utf-8") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

st.title("🛡️ AutoFuzzLLM")
st.caption("Automated Security Fuzzer for Large Language Models")

# Initialize and pull underlying computational context states
engines = get_core_engines()
prompt_data = initialize_application_state()

# Workspace Layout Navigation Setup
tab1, tab2 = st.tabs(["📊 Batch Fuzzing Campaign", "💬 Live Conversation Fuzzer"])

with tab1:
    render_batch_campaign_tab(prompt_data, engines)

with tab2:
    render_live_fuzzer_tab(engines)