# chart_page.py
import streamlit as st
import pandas as pd
import plotly.express as px

def render_chart_page():
    st.title("📊 Monthly Inventory Flow")

    if "official_data" not in st.session_state:
        st.warning("⚠️ No data found. Please upload files in the Data Loader page first.")
        return

    df_raw = st.session_state["official_data"].copy()

    # --- Sidebar filters ---
    st.sidebar.header("🔍 Filters")
    years = st.sidebar.multiselect("Year", sorted(df_raw["Year"].dropna().unique()))
    months = st.sidebar.multiselect("Month", sorted(df_raw["Month"].dropna().unique()))
    items = st.sidebar.multiselect("Item Code", df_raw["Item Code"].unique())

    df_filtered = df_raw.copy()
    if years:
        df_filtered = df_filtered[df_filtered["Year"].isin(years)]
    if months:
        df_filtered = df_filtered[df_filtered["Month"].isin(months)]
    if items:
        df_filtered = df_filtered[df_filtered["Item Code"].isin(items)]

    if df_filtered.empty:
        st.warning("⚠️ No data after filtering.")
        return

    # --- Take absolute values for Quantity[Unit1] ---
    df_filtered['Quantity[Unit1]'] = df_filtered['Quantity[Unit1]'].abs()

    # --- Aggregate by Month + Rcv So Flag ---
    chart_df = (
        df_filtered.groupby(["Month", "Rcv So Flag"], as_index=False)["Quantity[Unit1]"]
        .sum()
        .sort_values("Month")
    )

    # --- Line Chart ---
    fig = px.line(
        chart_df,
        x="Operation Date",
        y="Quantity[Unit1]",
        color="Rcv So Flag",
        markers=True,
        title="📈 Monthly Inbound vs Outbound (Positive Values Only)"
    )

    fig.update_layout(
        xaxis_title="Month",
        yaxis_title="Quantity",
        legend_title="Transaction Type",
        template="plotly_white"
    )

    st.plotly_chart(fig, use_container_width=True)
