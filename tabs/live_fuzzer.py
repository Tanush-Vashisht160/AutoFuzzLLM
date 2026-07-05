import streamlit as st
from fuzzing.campaign import FuzzCampaign

def render_live_fuzzer_tab(engines):
    """Manages chat context states and prints active runtime responses for target evaluations."""
    rule_engine = engines["rule_engine"]

    st.subheader("💬 Conversation Fuzzer (Chat Mode)")
    
    # Retrieve active provider state safely
    active_provider = "Llama2"
    if "campaign_providers" in st.session_state and st.session_state.campaign_providers:
        active_provider = st.session_state.campaign_providers[0]
        
    live_campaign = FuzzCampaign(active_provider)

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])
            if "risk" in msg and msg["role"] == "assistant":
                st.caption(f"Risk Evaluation Status Score: {msg['risk']}")

    user_input = st.chat_input("Type your attack prompt...", key="chat_interaction_input")
    
    if user_input:
        with st.chat_message("user"): 
            st.write(user_input)
        st.session_state.messages.append({"role": "user", "content": user_input})

        with st.spinner("Analyzing thread state context and responding..."):
            response_history = live_campaign.executor.run_conversation(st.session_state.messages)
            ai_text = response_history[-1]["response"] if isinstance(response_history, list) else response_history
            live_risk = rule_engine.analyze(ai_text)

        with st.chat_message("assistant"):
            st.write(ai_text)
            st.metric("Live Threat Assessment Level", live_risk)

        st.session_state.messages.append({"role": "assistant", "content": ai_text, "risk": live_risk})