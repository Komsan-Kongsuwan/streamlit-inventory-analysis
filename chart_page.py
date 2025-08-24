import streamlit as st
import pandas as pd
import plotly.express as px

def render_chart_page():
    st.title("📊 Inventory Flow by Operation Date")

    # Check if data exists
    if "official_data" not in st.session_state:
        st.warning("⚠️ No data found. Please upload files in the Data Loader page first.")
        return

    df_raw = st.session_state["official_data"].copy()

    # --- Year filter ---
    years_list = sorted(df_raw["Year"].dropna().unique())
    if "selected_year" not in st.session_state:
        st.session_state.selected_year = "ALL"

    # Radio buttons for year selection (horizontal)
    selected_year = st.radio(
        "Select Year",
        options=["ALL"] + [str(y) for y in years_list],
        index=0 if st.session_state.selected_year == "ALL" else years_list.tolist().index(st.session_state.selected_year) + 1,
        horizontal=True
    )
    st.session_state.selected_year = selected_year if selected_year != "ALL" else "ALL"

    if st.session_state.selected_year == "ALL":
        st.write("✅ Showing data for **All Years**")
    else:
        st.write(f"✅ Selected Year: **{st.session_state.selected_year}**")

    # --- Item filter ---
    items = st.multiselect("Item Code", df_raw["Item Code"].unique())

    # --- Apply filters ---
    df_filtered = df_raw.copy()
    if st.session_state.selected_year != "ALL":
        df_filtered = df_filtered[df_filtered["Year"] == int(st.session_state.selected_year)]
    if items:
        df_filtered = df_filtered[df_filtered["Item Code"].isin(items)]

    # --- Keep only Rcv(increase) ---
    df_filtered = df_filtered[df_filtered["Rcv So Flag"] == "Rcv(increase)"]

    if df_filtered.empty:
        st.warning("⚠️ No data after filtering.")
        return

    # --- Ensure positive Quantity ---
    df_filtered['Quantity[Unit1]'] = df_filtered['Quantity[Unit1]'].abs()

    # --- Aggregate by Period ---
    chart_df = df_filtered.groupby(["Period"], as_index=False)["Quantity[Unit1]"].sum()

    # --- Line Chart ---
    fig = px.line(
        chart_df,
        x="Period",
        y="Quantity[Unit1]",
        markers=True,
        title="📈 Inventory Flow Over Time"
        if st.session_state.selected_year == "ALL"
        else f"📈 Inventory Flow Over Time ({st.session_state.selected_year})"
    )

    fig.update_layout(
        xaxis_title="Period",
        yaxis_title="Quantity",
        template="plotly_white"
    )

    st.plotly_chart(fig, use_container_width=True)
