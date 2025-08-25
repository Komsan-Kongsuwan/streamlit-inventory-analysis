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

    # --- Sidebar: Year filter ---
    years_list = sorted(df_raw["Year"].dropna().unique())
    selected_year = st.sidebar.selectbox("Select Year", ["ALL"] + list(years_list), index=0)
    st.session_state.selected_year = selected_year

    # --- Sidebar: Month filter as buttons ---
    if "selected_month" not in st.session_state:
        st.session_state.selected_month = None
    selected_month = st.session_state.selected_month

    st.sidebar.markdown("### Select Month")
    month_cols = st.sidebar.columns(12, gap="small")
    for i, m in enumerate(range(1, 13)):
        if month_cols[i].button(calendar.month_abbr[m]):
            selected_month = m
            st.session_state.selected_month = selected_month

    # --- Main page: Item filter ---
    items = st.multiselect("Select Item Code", df_raw["Item Code"].unique())

    # --- Apply filters ---
    df_filtered = df_raw.copy()
    if selected_year != "ALL":
        df_filtered = df_filtered[df_filtered["Year"] == selected_year]
    if selected_month:
        df_filtered = df_filtered[df_filtered["Month"] == selected_month]  # assumes Month column exists
    if items:
        df_filtered = df_filtered[df_filtered["Item Code"].isin(items)]

    if df_filtered.empty:
        st.warning("⚠️ No data after filtering.")
        return

    # --- Keep only relevant categories ---
    df_filtered = df_filtered[df_filtered["Rcv So Flag"].isin(["Rcv(increase)", "So(decrese)"])]
    df_filtered['Quantity[Unit1]'] = df_filtered['Quantity[Unit1]'].abs()

    # --- Aggregate for bar chart ---
    if selected_month:
        chart_df = df_filtered.groupby(["Day", "Rcv So Flag"], as_index=False)["Quantity[Unit1]"].sum()
        x_label = "Day"
        title = f"📊 Daily Inventory in {selected_year}-{calendar.month_abbr[selected_month]}"
    elif selected_year != "ALL":
        chart_df = df_filtered.groupby(["Month", "Rcv So Flag"], as_index=False)["Quantity[Unit1]"].sum()
        x_label = "Month"
        title = f"📊 Monthly Inventory in {selected_year}"
    else:
        chart_df = df_filtered.groupby(["Year", "Rcv So Flag"], as_index=False)["Quantity[Unit1]"].sum()
        x_label = "Year"
        title = "📊 Yearly Inventory"

    chart_df = chart_df.sort_values(x_label)

    # --- Bar Chart ---
    fig_bar = px.bar(
        chart_df,
        x=x_label,
        y="Quantity[Unit1]",
        color="Rcv So Flag",
        barmode="group",
        title=title
    )
    fig_bar.update_layout(
        xaxis_title=x_label,
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
