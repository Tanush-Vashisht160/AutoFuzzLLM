import json
import streamlit as st
from analysis.risk_score import RiskScorer
from analysis.rule_engine import RuleEngine
from database.database import DatabaseManager
from analysis.response_classifier import ResponseClassifier
from analysis.owasp_mapper import OWASPMapper
from analysis.insights import InsightsEngine 

@st.cache_resource
def get_core_engines():
    """Initializes and caches core heavy compute scanning infrastructure engines."""
    return {
        "rule_engine": RuleEngine(),
        "risk_scorer": RiskScorer(),
        "classifier": ResponseClassifier(),
        "owasp": OWASPMapper(),
        "db": DatabaseManager(),
        "insights_engine": InsightsEngine()
    }

def initialize_application_state():
    """Validates runtime state history arrays and loads seed prompt datasets."""
    # Initialize Chat State History
    if "messages" not in st.session_state:
        st.session_state.messages = []
        
    # Load Prompt Dataset
    try:
        with open("datasets/seed_prompts.json", "r") as file:
            prompt_data = json.load(file)
    except FileNotFoundError:
        prompt_data = {}
        st.error("Critical Error: 'datasets/seed_prompts.json' dataset file could not be found.")
        
    return prompt_data