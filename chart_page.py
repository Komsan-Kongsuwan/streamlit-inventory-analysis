# chart_page.py
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

    # --- Year Buttons ---
    years_list = sorted(df_raw["Year"].dropna().unique())

    if "selected_year" not in st.session_state:
        st.session_state.selected_year = years_list[0]  # default first year

    cols = st.columns(len(years_list))
    for i, yr in enumerate(years_list):
        if cols[i].button(str(yr)):
            st.session_state.selected_year = yr

    selected_year = st.session_state.selected_year
    st.write(f"✅ Selected Year: **{selected_year}**")

    # --- Item filter ---
    items = st.multiselect("Item Code", df_raw["Item Code"].unique())

    # --- Apply filters ---
    df_filtered = df_raw.copy()
    if selected_year:
        df_filtered = df_filtered[df_filtered["Year"] == selected_year]
    if items:
        df_filtered = df_filtered[df_filtered["Item Code"].isin(items)]

    # --- Keep only Rcv(increase) ---
    df_filtered = df_filtered[df_filtered["Rcv So Flag"] == "Rcv(increase)"]

    if df_filtered.empty:
        st.warning("⚠️ No data after filtering.")
        return

    # --- Take absolute values for Quantity[Unit1] ---
    df_filtered['Quantity[Unit1]'] = df_filtered['Quantity[Unit1]'].abs()

    # --- Aggregate by Period ---
    chart_df = (
        df_filtered.groupby(["Period"], as_index=False)["Quantity[Unit1]"]
        .sum()
    )

    # --- Line Chart ---
    fig = px.line(
        chart_df,
        x="Period",
        y="Quantity[Unit1]",
        markers=True,
        title=f"📈 Inventory Flow Over Time ({selected_year})"
    )

    fig.update_layout(
        xaxis_title="Operation Date",
        yaxis_title="Quantity",
        template="plotly_white"
    )

    st.plotly_chart(fig, use_container_width=True)
