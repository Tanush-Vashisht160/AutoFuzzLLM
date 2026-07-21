import sqlite3
import pandas as pd
import streamlit as st
import glob
import json

st.title("📜 Campaign History")
# ----------------------------
# Saved JSON Reports
# ----------------------------

history_files = sorted(
    glob.glob("reports/history/*.json"),
    reverse=True
)
# ----------------------------
# Connect Database
# ----------------------------

conn = sqlite3.connect("autofuzz.db")

campaigns = pd.read_sql_query(
    "SELECT * FROM campaigns",
    conn
)
results = pd.read_sql_query(
    "SELECT * FROM results",
    conn
)

# ----------------------------
# No Campaigns
# ----------------------------

if campaigns.empty:
    st.info("No campaigns found.")
    st.stop()

# ----------------------------
# Campaign Selector
# ----------------------------

campaign_options = campaigns["id"].tolist()

selected_campaign = st.selectbox(
    "Select Campaign",
    campaign_options
)

# ----------------------------
# Selected Campaign Details
# ----------------------------

campaign = campaigns[
    campaigns["id"] == selected_campaign
].iloc[0]

st.subheader("Campaign Information")

col1, col2 = st.columns(2)

with col1:
    st.metric(
        "Campaign ID",
        campaign["id"]
    )

with col2:
    st.metric(
        "Provider",
        campaign["provider"]
    )

st.write("Created At")

st.info(
    campaign["created_at"]
)

st.write("Seed Prompt")

st.code(
    campaign["seed_prompt"]
)
# ----------------------------
# JSON Report Viewer
# ----------------------------

st.markdown("---")

st.subheader("Saved Report")

if history_files:

    selected_report = st.selectbox(
        "Saved JSON Reports",
        history_files
    )

    with open(selected_report, "r", encoding="utf-8") as file:

        report = json.load(file)

    st.subheader("Configuration")

    st.json(
        report["config"]
    )

    st.subheader("Summary")

    st.json(
        report["summary"]
    )

else:

    st.info("No saved JSON reports found.")
# ----------------------------
# Campaign Results
# ----------------------------

campaign_results = results[
    results["campaign_id"] == selected_campaign
]

st.subheader("Results")

st.dataframe(
    campaign_results,
    use_container_width=True
)

conn.close()