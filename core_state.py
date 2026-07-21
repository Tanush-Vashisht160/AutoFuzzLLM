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

    if "messages" not in st.session_state:
        st.session_state.messages = []

    return {}