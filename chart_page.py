import streamlit as st
import pandas as pd
import plotly.express as px
import calendar

def render_chart_page():
    st.title("📊 Inventory Flow by Operation Date")

    if "official_data" not in st.session_state:
        st.warning("⚠️ No data found. Please upload files in the Data Loader page first.")
        return

    df_raw = st.session_state["official_data"].copy()
    
    # --- Sidebar Filters ---
    st.sidebar.header("🔍 Filters")

    # Year filter
    years_list = sorted(df_raw["Year"].dropna().unique())
    selected_year = st.sidebar.selectbox("Select Year", ["ALL"] + years_list, index=0)

    # Month filter as buttons (side-by-side)
    selected_month = st.sidebar.session_state.get("selected_month", None)
    month_cols = st.sidebar.columns(12, gap="small")
    for i, m in enumerate(range(1, 13)):
        if month_cols[i].button(calendar.month_abbr[m]):
            selected_month = m
            st.sidebar.session_state.selected_month = selected_month

    # --- Item filter (main page) ---
    items = st.multiselect("Item Code", df_raw["Item Code"].unique())

    # --- Apply filters ---
    df_filtered = df_raw.copy()
    if selected_year != "ALL":
        df_filtered = df_filtered[df_filtered["Year"] == selected_year]
    if selected_month:
        df_filtered = df_filtered[df_filtered["Month"] == selected_month]
    if items:
        df_filtered = df_filtered[df_filtered["Item Code"].isin(items)]

    if df_filtered.empty:
        st.warning("⚠️ No data after filtering.")
        return

    # Keep only relevant categories
    df_filtered = df_filtered[df_filtered["Rcv So Flag"].isin(["Rcv(increase)", "So(decrese)"])]
    df_filtered['Quantity[Unit1]'] = df_filtered['Quantity[Unit1]'].abs()

    # --- Aggregate data for bar chart ---
    if selected_month:
        # Daily aggregation
        chart_df = df_filtered.groupby(["Day", "Rcv So Flag"], as_index=False)["Quantity[Unit1]"].sum()
        chart_df = chart_df.sort_values("Day")
    else:
        # Monthly aggregation
        chart_df = df_filtered.groupby(["Month", "Rcv So Flag"], as_index=False)["Quantity[Unit1]"].sum()
        chart_df = chart_df.sort_values("Month")

    # --- Chart title ---
    if selected_month:
        chart_title = f"📊 Daily Inventory in {selected_year}-{calendar.month_abbr[selected_month]}"
        x_col = "Day"
    else:
        chart_title = f"📊 Inventory in {selected_year} by Month"
        x_col = "Month"

    # --- Bar Chart ---
    fig_bar = px.bar(
        chart_df,
        x=x_col,
        y="Quantity[Unit1]",
        color="Rcv So Flag",
        barmode="group",
        title=chart_title
    )
    fig_bar.update_layout(
        xaxis_title=x_col,
        yaxis_title="Quantity",
        template="plotly_white",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.3,
            xanchor="center",
            x=0.5
        )
    )

    st.plotly_chart(fig_bar, use_container_width=True)
