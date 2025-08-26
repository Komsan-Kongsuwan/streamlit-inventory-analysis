import streamlit as st
import pandas as pd
import plotly.express as px
import calendar

def day_suffix(d):
    """Return day with suffix like 1st, 2nd, 3rd, 4th ..."""
    if 11 <= d <= 13:
        return f"{d}th"
    last_digit = d % 10
    if last_digit == 1:
        return f"{d}st"
    elif last_digit == 2:
        return f"{d}nd"
    elif last_digit == 3:
        return f"{d}rd"
    else:
        return f"{d}th"

def render_chart_page():
    # --- Reduce top and side margins/paddings of the page ---
    st.markdown("""
        <style>
            .block-container {
                padding-top: 1.5rem;
                padding-left: 1rem;
                padding-right: 1rem;
                padding-bottom: 0rem;
            }
        </style>
    """, unsafe_allow_html=True)

    st.title("📊 Inventory Flow by Operation Date")

    if "official_data" not in st.session_state:
        st.warning("⚠️ No data found. Please upload files in the Data Loader page first.")
        return

    df_raw = st.session_state["official_data"].copy()

    # --- Sidebar: Year filter ---
    years_list = sorted(df_raw["Year"].dropna().unique())
    selected_year = st.sidebar.selectbox("Select Year", ["ALL"] + list(years_list), index=0)

    # --- Sidebar: Month filter ---
    months = list(range(1, 13))
    selected_month = st.sidebar.radio(
        "Select Month (optional)",
        ["All"] + [calendar.month_abbr[m] for m in months],
        index=0
    )
    if selected_month != "All":
        selected_month_num = list(calendar.month_abbr).index(selected_month)
    else:
        selected_month_num = None

    # --- Main page: Item filter ---
    items = st.multiselect("Item Code", df_raw["Item Code"].unique())

    # --- Apply filters ---
    df_filtered = df_raw.copy()
    if selected_year != "ALL":
        df_filtered = df_filtered[df_filtered["Year"] == selected_year]
    if selected_month_num:
        df_filtered = df_filtered[df_filtered["Month"] == selected_month_num]
    if items:
        df_filtered = df_filtered[df_filtered["Item Code"].isin(items)]

    if df_filtered.empty:
        st.warning("⚠️ No data after filtering.")
        return

    # --- Keep relevant categories and absolute value ---
    df_filtered = df_filtered[df_filtered["Rcv So Flag"].isin(["Rcv(increase)", "So(decrese)"])]
    df_filtered['Quantity[Unit1]'] = df_filtered['Quantity[Unit1]'].abs()


    # ==========================================================
    # 📌 INFO BOX SECTION
    # ==========================================================

    # 1. Total item_code of all data
    total_item_codes = df_raw["Item Code"].nunique()

    # 2. Movement and non-movement item_code of all data
    # --- Determine latest 12 months ---
    df_raw['YearMonth'] = df_raw['Year']*100 + df_raw['Month']  # e.g., 202508
    latest_yearmonth = df_raw['YearMonth'].max()
    # Get the 12 latest months
    last_12_months = df_raw['YearMonth'].sort_values().unique()[-12:]
    df_last12 = df_raw[df_raw['YearMonth'].isin(last_12_months)]
    
    # Movement = appears at least once in Rcv or So during latest 12 months
    active_items = df_last12[df_last12["Rcv So Flag"].isin(["Rcv(increase)", "So(decrese)"])]["Item Code"].unique()
    movement_items = len(active_items)
    
    # Non-movement = total items in dataset minus active items in last 12 months
    total_item_codes = df_raw["Item Code"].nunique()
    non_movement_items = total_item_codes - movement_items
    
    # 3. New item_code of selection period (not seen before this year/month)
    if selected_year != "ALL":
        prev_data = df_raw[df_raw["Year"] < selected_year]
        if selected_month_num:
            prev_data = pd.concat([
                prev_data,
                df_raw[(df_raw["Year"] == selected_year) & (df_raw["Month"] < selected_month_num)]
            ])
        prev_items = set(prev_data["Item Code"].unique())
        new_items = set(df_filtered["Item Code"].unique()) - prev_items
        new_item_codes = len(new_items)
    else:
        new_item_codes = 0

    # 4. Day rcv and so of selection period
    day_rcv = df_filtered[df_filtered["Rcv So Flag"] == "Rcv(increase)"]["Day"].nunique() if "Day" in df_filtered else 0
    day_so = df_filtered[df_filtered["Rcv So Flag"] == "So(decrese)"]["Day"].nunique() if "Day" in df_filtered else 0

    # 5. Item_code rcv and so of selection period
    item_rcv = df_filtered[df_filtered["Rcv So Flag"] == "Rcv(increase)"]["Item Code"].nunique()
    item_so = df_filtered[df_filtered["Rcv So Flag"] == "So(decrese)"]["Item Code"].nunique()

    # 6. Amount rcv and so of selection period
    amount_rcv = df_filtered[df_filtered["Rcv So Flag"] == "Rcv(increase)"]["Quantity[Unit1]"].sum()
    amount_so = df_filtered[df_filtered["Rcv So Flag"] == "So(decrese)"]["Quantity[Unit1]"].sum()

    # --- Display info cards ---
    st.subheader("📦 Inventory Information")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Item Codes", total_item_codes)
        st.metric("Movement Items", movement_items)
        st.metric("Non-Movement Items", non_movement_items)
    with col2:
        st.metric("New Items (period)", new_item_codes)
        st.metric("Days with Rcv", day_rcv)
        st.metric("Days with So", day_so)
    with col3:
        st.metric("Item Codes Rcv", item_rcv)
        st.metric("Item Codes So", item_so)
        st.metric("Amount Rcv / So", f"{amount_rcv:.0f} / {amount_so:.0f}")

    st.markdown("---")

    # ==========================================================
    # 📊 CHART SECTION
    # ==========================================================
    if selected_month_num:
        # Daily aggregation
        if "Day" not in df_filtered.columns and "Operation Date" in df_filtered.columns:
            df_filtered["Day"] = pd.to_datetime(df_filtered["Operation Date"]).dt.day
        elif "Day" not in df_filtered.columns:
            df_filtered["Day"] = 1

        total_days = pd.Series(range(1, 32))  # assume max 31
        chart_df = df_filtered.groupby(["Day", "Rcv So Flag"], as_index=False)["Quantity[Unit1]"].sum()
        all_days_flags = pd.MultiIndex.from_product([total_days, chart_df["Rcv So Flag"].unique()], names=["Day", "Rcv So Flag"])
        chart_df = chart_df.set_index(["Day", "Rcv So Flag"]).reindex(all_days_flags, fill_value=0).reset_index()
        chart_df["x_label"] = chart_df["Day"].apply(day_suffix)
        chart_title = f"📊 Daily Inventory in {selected_year}-{calendar.month_abbr[selected_month_num]}"

    elif selected_year != "ALL":
        # Monthly aggregation
        chart_df = df_filtered.groupby(["Month", "Rcv So Flag"], as_index=False)["Quantity[Unit1]"].sum()
        all_months_flags = pd.MultiIndex.from_product([months, chart_df["Rcv So Flag"].unique()], names=["Month", "Rcv So Flag"])
        chart_df = chart_df.set_index(["Month", "Rcv So Flag"]).reindex(all_months_flags, fill_value=0).reset_index()
        chart_df["x_label"] = chart_df["Month"].apply(lambda m: calendar.month_abbr[m])
        chart_title = f"📊 Monthly Inventory in {selected_year}"

    else:
        # Yearly aggregation
        chart_df = df_filtered.groupby(["Year", "Rcv So Flag"], as_index=False)["Quantity[Unit1]"].sum()
        chart_df["x_label"] = chart_df["Year"].astype(str)
        chart_title = "📊 Inventory by Year"

    # --- Bar chart ---
    fig_bar = px.bar(
        chart_df,
        x="x_label",
        y="Quantity[Unit1]",
        color="Rcv So Flag",
        barmode="group",
        title=chart_title
    )
    fig_bar.update_layout(
        xaxis_title="",
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
