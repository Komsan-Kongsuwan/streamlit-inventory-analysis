import streamlit as st
import pandas as pd
import plotly.express as px

def render_chart_page():
    st.title("📊 Inventory Flow by Operation Date")

    if "official_data" not in st.session_state:
        st.warning("⚠️ No data found. Please upload files in the Data Loader page first.")
        return

    df_raw = st.session_state["official_data"].copy()

    # --- Filters in main page body ---
    st.subheader("🔍 Filters")

    years_list = sorted(df_raw["Year"].dropna().unique())

    if "selected_year" not in st.session_state:
        st.session_state.selected_year = "ALL"  # default show all

    # --- Split page: left for buttons, right for dummy ---
    left_col, right_col = st.columns([1, 3])  # left column narrower

    with left_col:
        # Inline year buttons using a smaller layout
        btn_cols = st.columns(len(years_list) + 1, gap="small")  # gap="small" reduces spacing

        # Select All button
        if btn_cols[0].button("✅ All"):
            st.session_state.selected_year = "ALL"

        # Year buttons
        for i, yr in enumerate(years_list):
            if btn_cols[i + 1].button(str(yr)):
                st.session_state.selected_year = yr

    selected_year = st.session_state.selected_year

    if selected_year == "ALL":
        st.write("✅ Showing data for **All Years**")
    else:
        st.write(f"✅ Selected Year: **{selected_year}**")

    # --- Item filter ---
    items = st.multiselect("Item Code", df_raw["Item Code"].unique())

    # --- Apply filters ---
    df_filtered = df_raw.copy()
    if selected_year != "ALL":
        df_filtered = df_filtered[df_filtered["Year"] == selected_year]
    if items:
        df_filtered = df_filtered[df_filtered["Item Code"].isin(items)]

    # --- Keep only Rcv(increase) ---
    df_filtered = df_filtered[df_filtered["Rcv So Flag"] == "Rcv(increase)"]

    if df_filtered.empty:
        st.warning("⚠️ No data
