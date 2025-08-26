# chart_page.py
import streamlit as st
import pandas as pd
import plotly.express as px
import calendar

def render_chart_page(df_raw: pd.DataFrame):
    st.title("📊 Inventory Movement Analysis")

    # --- Sidebar filters ---
    st.sidebar.header("🔎 Filters")
    years = ["ALL"] + sorted(df_raw["Year"].unique().tolist())
    months = ["ALL"] + list(calendar.month_abbr[1:])
    categories = ["ALL", "Rcv increase + So decrease", "Rcv increase", "So decrease"]

    selected_year = st.sidebar.selectbox("Select Year", years)
    selected_month = st.sidebar.selectbox("Select Month", months)
    selected_category = st.sidebar.selectbox("Select Category", categories)

    # --- Apply filters ---
    df_filtered = df_raw.copy()

    if selected_year != "ALL":
        df_filtered = df_filtered[df_filtered["Year"] == selected_year]

    if selected_month != "ALL":
        month_num = list(calendar.month_abbr).index(selected_month)
        df_filtered = df_filtered[df_filtered["Month"] == month_num]

    if selected_category != "ALL":
        if selected_category == "Rcv increase + So decrease":
            df_filtered = df_filtered[df_filtered["Rcv So Flag"].isin(["Rcv(increase)", "So(decrese)"])]
        elif selected_category == "Rcv increase":
            df_filtered = df_filtered[df_filtered["Rcv So Flag"] == "Rcv(increase)"]
        elif selected_category == "So decrease":
            df_filtered = df_filtered[df_filtered["Rcv So Flag"] == "So(decrese)"]

    # --- Fill missing months/days ---
    if selected_month == "ALL":
        # group by month
        all_months = pd.DataFrame({"Month": range(1, 13)})
        chart_df = (
            df_filtered.groupby(["Year", "Month", "Rcv So Flag"])["Quantity[Unit1]"]
            .sum()
            .reset_index()
        )
        chart_df = (
            all_months.merge(chart_df, on="Month", how="left")
            .fillna(0)
        )
        chart_df["Month Name"] = chart_df["Month"].apply(lambda x: calendar.month_abbr[x])
    else:
        # group by day of month
        if not df_filtered.empty:
            max_day = df_filtered["Day"].max()
        else:
            max_day = 31
        all_days = pd.DataFrame({"Day": range(1, max_day + 1)})
        chart_df = (
            df_filtered.groupby(["Year", "Month", "Day", "Rcv So Flag"])["Quantity[Unit1]"]
            .sum()
            .reset_index()
        )
        chart_df = all_days.merge(chart_df, on="Day", how="left").fillna(0)

    # --- Summary Information ---
    st.subheader("ℹ️ Inventory Summary")

    # 1. Total item_code of all data
    total_items = df_raw["Item Code"].nunique()

    # 2. Movement vs Non-movement (12 months check based on selected year)
    if selected_year != "ALL":
        year_data = df_raw[df_raw["Year"] == selected_year].copy()
        # Keep only rcv and so
        year_data = year_data[year_data["Rcv So Flag"].isin(["Rcv(increase)", "So(decrese)"])]
        moved_items = year_data["Item Code"].unique()
        movement_count = len(moved_items)
        non_movement_count = total_items - movement_count
    else:
        movement_count = df_raw[df_raw["Rcv So Flag"].isin(["Rcv(increase)", "So(decrese)"])]["Item Code"].nunique()
        non_movement_count = total_items - movement_count

    # 3. New item_code in selection period
    new_items = df_filtered["Item Code"].nunique()

    # 4. Distinct days with Rcv and So in selection period
    days_rcv = df_filtered[df_filtered["Rcv So Flag"] == "Rcv(increase)"]["Operation Date"].nunique()
    days_so = df_filtered[df_filtered["Rcv So Flag"] == "So(decrese)"]["Operation Date"].nunique()

    # 5. Distinct item_code with Rcv and So in selection period
    items_rcv = df_filtered[df_filtered["Rcv So Flag"] == "Rcv(increase)"]["Item Code"].nunique()
    items_so = df_filtered[df_filtered["Rcv So Flag"] == "So(decrese)"]["Item Code"].nunique()

    # 6. Amount of Rcv and So in selection period
    amount_rcv = df_filtered[df_filtered["Rcv So Flag"] == "Rcv(increase)"]["Quantity[Unit1]"].sum()
    amount_so = df_filtered[df_filtered["Rcv So Flag"] == "So(decrese)"]["Quantity[Unit1]"].sum()

    # --- Display Info Boxes ---
    col1, col2, col3 = st.columns(3)
    with col1:
        st.info(f"**Total Item Codes:** {total_items}")
        st.info(f"**Movement Items:** {movement_count}")
        st.info(f"**Non-Movement Items:** {non_movement_count}")
    with col2:
        st.info(f"**New Items (Selected Period):** {new_items}")
        st.info(f"**Days with Rcv:** {days_rcv}")
        st.info(f"**Days with So:** {days_so}")
    with col3:
        st.info(f"**Item Codes with Rcv:** {items_rcv}")
        st.info(f"**Item Codes with So:** {items_so}")
        st.info(f"**Rcv Amount:** {amount_rcv:,.0f}")
        st.info(f"**So Amount:** {amount_so:,.0f}")

    # --- Visualization ---
    st.subheader("📈 Bar Chart")

    if selected_month == "ALL":
        fig_bar = px.bar(
            chart_df,
            x="Month Name",
            y="Quantity[Unit1]",
            color="Rcv So Flag",
            barmode="stack",
            title="Monthly Rcv vs So"
        )
    else:
        fig_bar = px.bar(
            chart_df,
            x="Day",
            y="Quantity[Unit1]",
            color="Rcv So Flag",
            barmode="stack",
            title="Daily Rcv vs So"
        )
    st.plotly_chart(fig_bar, use_container_width=True)

    # --- Table View ---
    st.subheader("📋 Data Table")
    if selected_month == "ALL":
        table = chart_df.pivot_table(
            index="Rcv So Flag",
            columns="Month Name",
            values="Quantity[Unit1]",
            aggfunc="sum",
            fill_value=0
        )
    else:
        table = chart_df.pivot_table(
            index="Rcv So Flag",
            columns="Day",
            values="Quantity[Unit1]",
            aggfunc="sum",
            fill_value=0
        )
    st.dataframe(table)
