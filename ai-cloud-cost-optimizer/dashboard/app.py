import streamlit as st
import pandas as pd
import plotly.express as px
import sys
import os

# Add parent directory to path to import local modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.cost_analysis import load_data, analyze_costs, detect_anomalies
from ai_engine.recommendation_engine import generate_recommendations

# Set page config
st.set_page_config(page_title="AI Cloud Cost Optimizer", layout="wide")

st.title("🚀 AI Cloud Cost Optimization Platform")
st.markdown("Analyze AWS cloud usage data and detect cost optimization opportunities.")

# Sidebar - Data Source
st.sidebar.header("Data Source")
data_path = "data/sample_cost_data.csv"
if not os.path.exists(data_path):
    # Fallback to absolute path if running from different dir
    data_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data/sample_cost_data.csv")

try:
    df = load_data(data_path)
    analysis = analyze_costs(df)
    anomalies = detect_anomalies(df)
    recommendations = generate_recommendations(anomalies, df)

    # Top Level Metrics
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Monthly Cost", f"${analysis['total_cost']:,.2f}")
    col2.metric("Detected Anomalies", len(anomalies))
    col3.metric("Cost Savings Opportunities", len(recommendations))

    # Visualization Layer
    st.divider()
    c1, c2 = st.columns(2)

    with c1:
        st.subheader("Cost by AWS Service")
        fig_bar = px.bar(analysis['service_costs'], x='service_name', y='monthly_cost', 
                         color='service_name', title="Monthly Spending per Service")
        st.plotly_chart(fig_bar, use_container_width=True)

    with c2:
        st.subheader("Cost Trend Over Time")
        fig_line = px.line(analysis['daily_costs'], x='timestamp', y='monthly_cost', 
                           title="Daily Spending Trend")
        st.plotly_chart(fig_line, use_container_width=True)

    # Anomalies and Recommendations
    st.divider()
    st.subheader("⚠️ Detected Anomalies")
    if anomalies:
        for anomaly in anomalies:
            with st.expander(f"{anomaly['type']}: {anomaly['resource_id']} ({anomaly['service']})"):
                st.write(f"**Details:** {anomaly['details']}")
                if 'cost' in anomaly:
                    st.write(f"**Cost:** ${anomaly['cost']:.2f}")
                if 'cpu_usage' in anomaly:
                    st.write(f"**CPU Usage:** {anomaly['cpu_usage']}%")
    else:
        st.success("No anomalies detected!")

    st.subheader("💡 Optimization Recommendations")
    if recommendations:
        for rec in recommendations:
            st.info(f"**{rec['problem']}**")
            st.write(f"**Recommended Action:** {rec['action']}")
            st.write(f"**Estimated Monthly Savings:** `${rec['estimated_savings']:.2f}`")
            st.divider()
    else:
        st.success("Your infrastructure is fully optimized!")

except Exception as e:
    st.error(f"Error loading dashboard: {e}")
    st.write(f"Current working directory: {os.getcwd()}")
    st.write(f"Attempted data path: {data_path}")
