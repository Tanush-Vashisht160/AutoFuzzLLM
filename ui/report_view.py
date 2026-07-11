import streamlit as st
from reports.report_generator import ReportGenerator
import streamlit as st
from reports.report_generator import ReportGenerator


@st.cache_data(show_spinner=False)
def generate_pdf(campaign_id, results):
    generator = ReportGenerator()
    generator.create_pdf(
        "campaign_report.pdf",
        campaign_id,
        results
    )

    with open("campaign_report.pdf", "rb") as f:
        return f.read()
    
def render_artifact_exports(campaign_id, results, df):
    """
    Renders the raw interactive dataframe, handles CSV downloads, 
    and handles background PDF compilation.
    """
    st.subheader("Campaign Results")
    st.dataframe(df, use_container_width=True)

    csv = df.to_csv(index=False)
    st.download_button(
        "📊 Download CSV Table",
        csv,
        file_name="campaign_results.csv",
        mime="text/csv"
    )

    st.markdown("---")
    st.subheader("Export Campaign Artifacts")
    
    pdf_bytes = generate_pdf(campaign_id, results)

    st.download_button(
        "📄 Download PDF Report",
        data=pdf_bytes,
        file_name="campaign_report.pdf",
        mime="application/pdf",
        on_click="ignore"
    )


def show_report(summary):
    """
    Renders the executive summary metrics dashboard and the 
    high-level recommendation engine view.
    """
    st.header("📄 Security Assessment Report")

    st.markdown("## Executive Summary")
    st.write(summary["executive"])

    st.markdown("---")
    st.subheader("Models Tested")
    st.write(", ".join(summary["models"]))

    # Metric layout inside columns for better utilization of screen width
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.metric("Average Risk", summary["average"])
    with col2:
        st.metric("Total Tests", summary["tests"])
    with col3:
        st.metric("Critical", summary["critical"])
    with col4:
        st.metric("Warnings", summary["warning"])
    with col5:
        st.metric("Safe", summary["safe"])

    st.markdown("---")
    st.subheader("Recommendations")
    for rec in summary["recommendations"]:
        st.write("•", rec)

    #st.success("The downloadable PDF below contains the same information in printable format.")