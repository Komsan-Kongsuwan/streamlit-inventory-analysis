import streamlit as st
import pandas as pd
import plotly.express as px

def render_chart_page():
    st.title("📊 Inventory Flow by Operation Date")

    if "official_data" not in st.session_state:
        st.warning("⚠️ No data found. Please upload files in the Data Loader page first.")
        return

    df_raw = st.session_state["official_data"].copy()
    df_raw['Rcv So Flag'] = df_raw['Rcv So Flag'].str.strip()
    years_list = sorted(df_raw["Year"].dropna().unique())

    st.subheader("🔍 Filters")

    # --- Year selection with radio buttons (inline, button-like) ---
    if "selected_year" not in st.session_state:
        st.session_state.selected_year = "ALL"

    year_options = ["ALL"] + [str(y) for y in years_list]
    st.session_state.selected_year = st.radio(
        "Select Year:",
        options=year_options,
        index=0 if st.session_state.selected_year=="ALL" else year_options.index(str(st.session_state.selected_year)),
        horizontal=True
    )

    selected_year = st.session_state.selected_year
    st.write(f"✅ Selected Year: **{selected_year}**" if selected_year != "ALL" else "✅ Showing data for **All Years**")

    # --- Item filter ---
    items = st.multiselect("Item Code", df_raw["Item Code"].unique())

    # --- Apply filters ---
    df_filtered = df_raw.copy()
    if selected_year != "ALL":
        df_filtered = df_filtered[df_filtered["Year"] == int(selected_year)]
    if items:
        df_filtered = df_filtered[df_filtered["Item Code"].isin(items)]

    # --- Keep only Rcv(increase) ---
    df_filtered = df_filtered[df_filtered["Rcv So Flag"] == "Rcv(increase)"]

    if df_filtered.empty:
        st.warning("⚠️ No data after filtering.")
        return

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
        if selected_year == "ALL"
        else f"📈 Inventory Flow Over Time ({selected_year})"
    )

    fig.update_layout(
        xaxis_title="Period",
        yaxis_title="Quantity",
        template="plotly_white"
    )

    st.plotly_chart(fig, use_container_width=True)

