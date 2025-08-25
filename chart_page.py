import streamlit as st
import pandas as pd
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

    # --- Sidebar: Month filter (vertical radio buttons) ---
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

    # --- Keep relevant categories and absolute quantity ---
    df_filtered = df_filtered[df_filtered["Rcv So Flag"].isin(["Rcv(increase)", "So(decrese)"])]
    df_filtered['Quantity[Unit1]'] = df_filtered['Quantity[Unit1]'].abs()

    # --- Determine aggregation level ---
    if selected_month_num:
        # Daily aggregation
        if "Day" not in df_filtered.columns and "Operation Date" in df_filtered.columns:
            df_filtered["Day"] = pd.to_datetime(df_filtered["Operation Date"]).dt.day
        elif "Day" not in df_filtered.columns:
            df_filtered["Day"] = 1  # fallback
        table_df = df_filtered.groupby(["Day", "Rcv So Flag", "Item Code"], as_index=False)["Quantity[Unit1]"].sum()
        table_title = f"📋 Daily Inventory in {selected_year}-{calendar.month_abbr[selected_month_num]}"
    elif selected_year != "ALL":
        # Monthly aggregation for selected year
        table_df = df_filtered.groupby(["Month", "Rcv So Flag", "Item Code"], as_index=False)["Quantity[Unit1]"].sum()
        table_title = f"📋 Monthly Inventory in {selected_year}"
    else:
        # Yearly aggregation
        table_df = df_filtered.groupby(["Year", "Rcv So Flag", "Item Code"], as_index=False)["Quantity[Unit1]"].sum()
        table_title = "📋 Inventory by Year"

    st.subheader(table_title)
    st.dataframe(table_df.sort_values(table_df.columns[0]))
