import streamlit as st
import pandas as pd
import plotly.express as px

def render_chart_page():
    st.title("📊 Inventory Flow by Operation Date")

    if "official_data" not in st.session_state:
        st.warning("⚠️ No data found. Please upload files in the Data Loader page first.")
        return

    df_raw = st.session_state["official_data"].copy()
    years_list = sorted(df_raw["Year"].dropna().unique())

    # keep state
    if "selected_year" not in st.session_state:
        st.session_state.selected_year = "ALL"

    st.write("🔍 **Select Year**")

    # inline button row with small gap
    cols = st.columns(len(years_list) + 1, gap="small")

    # ALL button
    if cols[0].button("ALL", key="year_all"):
        st.session_state.selected_year = "ALL"

    # year buttons
    for i, yr in enumerate(years_list, start=1):
        if cols[i].button(str(yr), key=f"year_{yr}"):
            st.session_state.selected_year = yr

    selected_year = st.session_state.selected_year

    if selected_year == "ALL":
        st.write("✅ Showing data for **All Years**")
    else:
        st.write(f"✅ Selected Year: **{selected_year}**")

    # Item filter
    items = st.multiselect("Item Code", df_raw["Item Code"].unique())

    # Apply filters
    df_filtered = df_raw.copy()
    if selected_year != "ALL":
        df_filtered = df_filtered[df_filtered["Year"] == selected_year]
    if items:
        df_filtered = df_filtered[df_filtered["Item Code"].isin(items)]

    df_filtered = df_filtered[df_filtered["Rcv So Flag"] == "Rcv(increase)"]

    if df_filtered.empty:
        st.warning("⚠️ No data after filtering.")
        return

    df_filtered['Quantity[Unit1]'] = df_filtered['Quantity[Unit1]'].abs()

    chart_df = (
        df_filtered.groupby(["Period"], as_index=False)["Quantity[Unit1]"]
        .sum()
    )

    fig = px.line(
        chart_df,
        x="Period",
        y="Quantity[Unit1]",
        markers=True,
        title="📈 Inventory Flow Over Time"
        if selected_year == "ALL"
        else f"📈 Inventory Flow Over Time ({selected_year})"
    )

    st.plotly_chart(fig, use_container_width=True)
