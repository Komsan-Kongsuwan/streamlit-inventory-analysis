# chart_page.py
import streamlit as st
import plotly.express as px
import pandas as pd

def render_chart_page():
    st.title("📊 Inventory Charts")

    if "official_data" not in st.session_state:
        st.warning("⚠️ No data found. Please upload files in the Data Upload page first.")
        return

    df_raw = st.session_state["official_data"]

    # ✅ Filters
    st.sidebar.header("🔍 Filters")
    owners = st.sidebar.multiselect("Owner Name", df_raw["Owner Name"].unique())
    items = st.sidebar.multiselect("Item Code", df_raw["Item Code"].unique())
    years = st.sidebar.multiselect("Year", df_raw["Year"].unique())
    months = st.sidebar.multiselect("Month", sorted(df_raw["Month"].unique()))

    df_filtered = df_raw.copy()
    if owners:
        df_filtered = df_filtered[df_filtered["Owner Name"].isin(owners)]
    if items:
        df_filtered = df_filtered[df_filtered["Item Code"].isin(items)]
    if years:
        df_filtered = df_filtered[df_filtered["Year"].isin(years)]
    if months:
        df_filtered = df_filtered[df_filtered["Month"].isin(months)]

    if df_filtered.empty:
        st.warning("⚠️ No data after filtering.")
        return

    # --- Chart 1: Quantity by Month ---
    monthly_summary = (
        df_filtered.groupby(["Year", "Month"], as_index=False)["Quantity[Unit1]"].sum()
    )
    monthly_summary["MonthName"] = monthly_summary["Month"].apply(
        lambda x: pd.to_datetime(str(x), format="%m").strftime("%b")
    )

    fig1 = px.bar(
        monthly_summary,
        x="MonthName",
        y="Quantity[Unit1]",
        color="Year",
        barmode="group",
        title="Monthly Received Quantity",
    )
    st.plotly_chart(fig1, use_container_width=True)

    # --- Chart 2: Top Items ---
    item_summary = (
        df_filtered.groupby(["Item Code", "Item Name"], as_index=False)["Quantity[Unit1]"].sum()
        .sort_values("Quantity[Unit1]", ascending=False)
        .head(10)
    )

    fig2 = px.bar(
        item_summary,
        x="Item Code",
        y="Quantity[Unit1]",
        color="Item Name",
        title="Top 10 Items by Quantity",
    )
    st.plotly_chart(fig2, use_container_width=True)

    # --- Chart 3: Owner-wise Distribution ---
    owner_summary = (
        df_filtered.groupby(["Owner Name"], as_index=False)["Quantity[Unit1]"].sum()
        .sort_values("Quantity[Unit1]", ascending=False)
    )

    fig3 = px.pie(
        owner_summary,
        names="Owner Name",
        values="Quantity[Unit1]",
        title="Owner Contribution",
    )
    st.plotly_chart(fig3, use_container_width=True)
