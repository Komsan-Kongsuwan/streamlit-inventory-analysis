# chart_page.py
import streamlit as st
import pandas as pd
import plotly.express as px
import calendar

def render_chart_page():
    st.title("📊 Inventory Visualization")

    # --- Load data from session state ---
    if "official_data" not in st.session_state:
        st.warning("⚠️ Official data not loaded. Please upload data first.")
        return
    df = st.session_state["official_data"]

    # --- Extract Year / Month ---
    df["Year"] = pd.to_datetime(df["Document Date"]).dt.year
    df["Month"] = pd.to_datetime(df["Document Date"]).dt.month
    df["Day"] = pd.to_datetime(df["Document Date"]).dt.day

    # --- Sidebar filters ---
    st.sidebar.header("🔎 Filters")

    # Year filter
    years = sorted(df["Year"].unique())
    year_options = ["ALL"] + years
    selected_year = st.sidebar.selectbox("Select Year", year_options)

    # Month filter
    if selected_year == "ALL":
        month_options = ["ALL"]
    else:
        month_options = ["ALL"] + [calendar.month_abbr[m] for m in range(1, 13)]
    selected_month = st.sidebar.selectbox("Select Month", month_options)

    # Category filter
    cat_options = ["ALL", "Rcv increase", "So decrese"]
    selected_cat = st.sidebar.selectbox("Select Category", cat_options)

    # --- Apply filters ---
    df_filtered = df.copy()
    if selected_year != "ALL":
        df_filtered = df_filtered[df_filtered["Year"] == selected_year]
    if selected_month != "ALL":
        selected_month_num = list(calendar.month_abbr).index(selected_month)
        df_filtered = df_filtered[df_filtered["Month"] == selected_month_num]
    else:
        selected_month_num = None
    if selected_cat != "ALL":
        df_filtered = df_filtered[df_filtered["Rcv So Flag"] == selected_cat]

    # --- Grouped Data ---
    if selected_month_num:  # Daily
        chart_df = df_filtered.groupby(["Day", "Rcv So Flag"], as_index=False)["Quantity[Unit1]"].sum()
        # ensure all days exist
        all_days = pd.DataFrame({"Day": range(1, 32)})
        chart_df = all_days.merge(chart_df, on="Day", how="left").fillna(0)
    elif selected_year != "ALL":  # Monthly
        chart_df = df_filtered.groupby(["Month", "Rcv So Flag"], as_index=False)["Quantity[Unit1]"].sum()
        # ensure all months exist
        all_months = pd.DataFrame({"Month": range(1, 13)})
        chart_df = all_months.merge(chart_df, on="Month", how="left").fillna(0)
    else:  # Yearly
        chart_df = df_filtered.groupby(["Year", "Rcv So Flag"], as_index=False)["Quantity[Unit1]"].sum()

    # --- Bar Chart ---
    if selected_month_num:  # Daily
        fig_bar = px.bar(
            chart_df,
            x="Day",
            y="Quantity[Unit1]",
            color="Rcv So Flag",
            barmode="stack",
            title=f"Daily Quantity in {selected_month} {selected_year}"
        )
    elif selected_year != "ALL":  # Monthly
        chart_df["MonthName"] = chart_df["Month"].apply(lambda x: calendar.month_abbr[x])
        fig_bar = px.bar(
            chart_df,
            x="MonthName",
            y="Quantity[Unit1]",
            color="Rcv So Flag",
            barmode="stack",
            title=f"Monthly Quantity in {selected_year}"
        )
    else:  # Yearly
        fig_bar = px.bar(
            chart_df,
            x="Year",
            y="Quantity[Unit1]",
            color="Rcv So Flag",
            barmode="stack",
            title="Yearly Quantity"
        )

    st.plotly_chart(fig_bar, use_container_width=True)

    # --- Pivot Table ---
    if selected_month_num:  # Daily pivot
        table_df = chart_df.pivot(index="Rcv So Flag", columns="Day", values="Quantity[Unit1]").fillna(0).reset_index()
    elif selected_year != "ALL":  # Monthly pivot
        table_df = chart_df.pivot(index="Rcv So Flag", columns="Month", values="Quantity[Unit1]").fillna(0).reset_index()
        # rename columns to month abbrev
        table_df.columns = ["Rcv So Flag"] + [calendar.month_abbr[m] for m in table_df.columns[1:]]
    else:  # Yearly pivot
        table_df = chart_df.pivot(index="Rcv So Flag", columns="Year", values="Quantity[Unit1]").fillna(0).reset_index()

    st.subheader("📋 Pivot Table")
    st.dataframe(table_df, use_container_width=True)
