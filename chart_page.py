# chart_page.py
import streamlit as st
import pandas as pd
import plotly.express as px

def render_chart_page():
    st.title("📊 Monthly Inventory Flow")

    if "official_data" not in st.session_state:
        st.warning("⚠️ No data found. Please upload files in the Data Loader page first.")
        return

    df_raw = st.session_state["official_data"]

    # --- Aggregate by Month + Rcv So Flag ---
    chart_df = (
        df_raw.groupby(["Month", "Rcv So Flag"], as_index=False)["Quantity[Unit1]"]
        .sum()
        .sort_values("Month")
    )

    # --- Line Chart ---
    fig = px.line(
        chart_df,
        x="Month",
        y="Quantity[Unit1]",
        color="Rcv So Flag",
        markers=True,
        title="📈 Monthly Inbound vs Outbound",
    )

    fig.update_layout(
        xaxis_title="Month",
        yaxis_title="Quantity",
        legend_title="Transaction Type",
        template="plotly_white"
    )

    st.plotly_chart(fig, use_container_width=True)
