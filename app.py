import json
from datetime import datetime
import pandas as pd
import streamlit as st

from analysis.risk_score import RiskScorer
from analysis.rule_engine import RuleEngine
from database.database import DatabaseManager
from fuzzing.campaign import FuzzCampaign
from reports.report_generator import ReportGenerator

st.set_page_config(page_title="AutoFuzzLLM", page_icon="🛡️", layout="wide")

st.title("🛡️ AutoFuzzLLM")
st.caption("Automated Security Fuzzer for Large Language Models")

# -------------------------------
# Load Prompt Dataset
# -------------------------------
with open("datasets/seed_prompts.json", "r") as file:
    prompt_data = json.load(file)

category_selection = st.selectbox("Attack Category", list(prompt_data.keys()))

seed_prompt = st.selectbox("Seed Prompt", prompt_data[category_selection])

num_mutations = st.slider("Maximum Mutations", min_value=1, max_value=11, value=11)

if st.button("🚀 Start Fuzzing Campaign"):

    campaign = FuzzCampaign()

    db = DatabaseManager()
    campaign_id = db.create_campaign(
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"), category_selection, seed_prompt
    )
    results = campaign.run(seed_prompt, max_tests=num_mutations)

    rule_engine = RuleEngine()
    risk_scorer = RiskScorer()

    st.success(f"Campaign Finished ({len(results)} Tests)")

    # 1️⃣ Initialize Campaign Statistics (Before the loop)
    attack_summary = {}  
    total = len(results)
    safe = 0
    warning = 0
    critical = 0
    scores = []
    table = []

    for i, result in enumerate(results[:num_mutations], start=1):

        # Handle score details evaluation based on result type
        # For multi-turn, we analyze the final assistant response in the chain
        if "conversation" in result and result["responses"]:
            final_response = result["responses"][-1]["response"]
            risk = rule_engine.analyze(final_response)
            details = risk_scorer.score(final_response)
        else:
            risk = rule_engine.analyze(result["response"])
            details = risk_scorer.score(result["response"])

        # Update the Campaign Statistics Loop with Category Counter
        category = result["category"]
        if category not in attack_summary:
            attack_summary[category] = 0
        attack_summary[category] += 1

        # 2️⃣ Update Campaign Statistics (Inside the loop)
        scores.append(details["score"])

        if details["severity"] == "Low":
            safe += 1
        elif details["severity"] == "Medium":
            warning += 1
        elif details["severity"] == "Critical":
            critical += 1

        # Determine prompt preview string for table visualization
        prompt_preview = (
            f"Multi-turn Conversation ({len(result['conversation'])} Turns)"
            if "conversation" in result
            else result["prompt"]
        )

        # Updated table format with "Category" column
        table.append({
            "Category": category,
            "Prompt": prompt_preview,
            "Score": details["score"],
            "Severity": details["severity"],
            "Status": details["status"]
        })

        # Save single-prompt or conversation tracking state into db safely
        db.save_result(
            campaign_id, 
            prompt_preview, 
            result["responses"][-1]["response"] if "conversation" in result else result["response"], 
            risk
        )

        with st.expander(f"Test {i} [{category}]"):
            # Show Category in Every Test Expander
            st.subheader("Attack Category")
            st.info(result["category"])

            # 🔄 Dynamic Branching: Multi-Turn Conversation Display vs Single Prompt
            if "conversation" in result:
                st.subheader("Conversation")
                for turn_idx, prompt in enumerate(result["conversation"], start=1):
                    st.markdown(f"**User {turn_idx}:**")
                    st.code(prompt)
                    st.markdown("**Assistant:**")
                    st.write(result["responses"][turn_idx - 1]["response"])
                    st.markdown("---")
            else:
                st.markdown("### Mutated Prompt")
                st.code(result["prompt"])

                st.markdown("### Model Response")
                st.write(result["response"])

            # Render UI metrics side-by-side inside expander block
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Risk Level", risk)
            with col2:
                st.metric("Risk Score", details["score"])

            # Output additional severity metadata
            st.write(f"**Severity:** {details['severity']}")
            st.write(f"**Status:** {details['status']}")

    # 3️⃣ Calculate Statistics (After the loop)
    if scores:
        average = sum(scores) / len(scores)
    else:
        average = 0

    st.markdown("---")

    # 4️⃣ Dashboard Summary Metrics
    st.subheader("Campaign Overview")
    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Total Tests", total)
    col2.metric("Safe", safe)
    col3.metric("Warning", warning)
    col4.metric("Critical", critical)
    col5.metric("Average Risk", round(average, 1))

    # Attack Summary Dashboard
    st.subheader("Attack Categories Tested")
    for category, count in attack_summary.items():
        st.write(f"**{category}** : {count} tests")

    # 5️⃣ Display Results Table & CSV Export
    df = pd.DataFrame(table)
    st.subheader("Campaign Results")
    st.dataframe(df, use_container_width=True)

    # CSV Export Button
    csv = df.to_csv(index=False)
    st.download_button(
        "📊 Download CSV",
        csv,
        file_name="campaign_results.csv",
        mime="text/csv"
    )

    # 6️⃣ Render Risk Distribution Chart
    chart = {
        "Low": safe,
        "Medium": warning,
        "Critical": critical
    }
    st.subheader("Risk Distribution")
    st.bar_chart(chart)

    # 7️⃣ PDF Report Generation Action
    st.markdown("---")
    st.subheader("Export Campaign Artifacts")
    
    generator = ReportGenerator()
    generator.create_pdf(
        "campaign_report.pdf",
        campaign_id,
        results
    )

    with open("campaign_report.pdf", "rb") as file:
        st.download_button(
            "📄 Download PDF Report",
            file,
            file_name="campaign_report.pdf"
        )