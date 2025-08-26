# chart_page.py
import streamlit as st
import pandas as pd
import plotly.express as px

def render_chart_page():
    st.title("📊 Inventory Movement Analysis")

    # --- Load data from session state ---
    if "inventory_data" not in st.session_state:
        st.warning("⚠️ No inventory data loaded. Please upload data first.")
        return

    df = st.session_state["inventory_data"].copy()

    # --- Ensure required columns exist ---
    required_cols = ["Year", "Month", "Day", "Item Code", "Rcv So Flag", "Quantity[Unit1]"]
    for col in required_cols:
        if col not in df.columns:
            st.error(f"❌ Missing column in data: {col}")
            return

    # --- Movement / Non-Movement filter ---
    item_summary = df.groupby("Item Code")["Quantity[Unit1]"].sum().reset_index()
    movement_items = item_summary[item_summary["Quantity[Unit1]"] > 0]["Item Code"].unique()
    non_movement_items = item_summary[item_summary["Quantity[Unit1]"] == 0]["Item Code"].unique()

    movement_option = st.radio(
        "Movement Filter",
        ["All", "Movement", "Non-Movement"],
        horizontal=True
    )

    if movement_option == "Movement":
        df = df[df["Item Code"].isin(movement_items)]
    elif movement_option == "Non-Movement":
        df = df[df["Item Code"].isin(non_movement_items)]

    # --- Year filter ---
    years = sorted(df["Year"].unique())
    year_option = st.selectbox("Select Year", ["All"] + years)
    if year_option != "All":
        df = df[df["Year"] == year_option]

    # --- Month filter ---
    months = list(range(1, 13))
    month_abbr = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
                  "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    month_map = dict(zip(months, month_abbr))

    month_option = st.selectbox("Select Month", ["All"] + month_abbr)
    if month_option != "All":
        selected_month = months[month_abbr.index(month_option)]
        df = df[df["Month"] == selected_month]

    # --- Category filter ---
    cat_option = st.selectbox(
        "Category (Rcv/So)",
        ["All", "Rcv increase", "So decrease"]
    )
    if cat_option != "All":
        df = df[df["Rcv So Flag"] == cat_option]

    if df.empty:
        st.warning("⚠️ No data available for the selected filters.")
        return

    # --- View Option (Chart / Table) ---
    view_option = st.radio("View as", ["Chart", "Table"], horizontal=True)

    if view_option == "Chart":
        # Group data
        chart_df = (
            df.groupby(["Month", "Rcv So Flag"], as_index=False)["Quantity[Unit1]"]
            .sum()
        )

        if chart_df.empty:
            st.warning("⚠️ No chart data to display.")
            return

        fig = px.bar(
            chart_df,
            x="Month",
            y="Quantity[Unit1]",
            color="Rcv So Flag",
            barmode="stack",
            category_orders={"Month": months},
            title="Inventory Movement by Month"
        )
        fig.update_layout(xaxis=dict(tickmode="array", tickvals=months, ticktext=month_abbr))
        st.plotly_chart(fig, use_container_width=True)

    else:  # Table view
        pivot_df = (
            df.groupby(["Month", "Rcv So Flag"])["Quantity[Unit1]"]
            .sum()
            .reset_index()
            .pivot(index="Rcv So Flag", columns="Month", values="Quantity[Unit1]")
            .fillna(0)
        )

        # Ensure all months appear
        pivot_df = pivot_df.reindex(columns=months, fill_value=0)
        pivot_df.columns = month_abbr  # rename to abbreviations

        st.dataframe(pivot_df, use_container_width=True)
