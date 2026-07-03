import sqlite3
import streamlit as st
import pandas as pd

st.title("📜 Campaign History")

conn = sqlite3.connect("autofuzz.db")

campaigns = pd.read_sql_query(
    "SELECT * FROM campaigns",
    conn
)

results = pd.read_sql_query(
    "SELECT * FROM results",
    conn
)

st.subheader("Campaigns")
st.dataframe(campaigns)

st.subheader("Results")
st.dataframe(results)
