import streamlit as st
import pandas as pd
import plotly.express as px

def render_chart_page():
    st.title("📊 Inventory Flow by Operation Date")

    if "official_data" not in st.session_state:
        st.warning("⚠️ No data found. Please upload files in the Data Loader page first.")
        return

    df_raw = st.session_state["official_data"].copy()

    # --- Sidebar Year filter ---
    years_list = sorted(df_raw["Year"].dropna().unique())
    selected_year = st.sidebar.radio(
        "Select Year",
        options=["ALL"] + years_list,
        index=0
    )

    # --- Item filter in main page ---
    items = st.multiselect("Item Code", df_raw["Item Code"].unique())

    st.write(
        f"✅ Showing data for **{selected_year}**"
        if selected_year != "ALL"
        else "✅ Showing data for **All Years**"
    )

    # --- Apply filters ---
    df_filtered = df_raw.copy()
    if selected_year != "ALL":
        df_filtered = df_filtered[df_filtered["Year"] == selected_year]
    if items:
        df_filtered = df_filtered[df_filtered["Item Code"].isin(items)]

    if df_filtered.empty:
        st.warning("⚠️ No data after filtering.")
        return

    # --- Keep only relevant categories ---
    df_filtered = df_filtered[df_filtered["Rcv So Flag"].isin(["Rcv(increase)", "So(decrese)"])]
    df_filtered['Quantity[Unit1]'] = df_filtered['Quantity[Unit1]'].abs()

    # --- Aggregate for bar chart ---
    if selected_year == "ALL":
        chart_df_bar = df_filtered.groupby(
            ["Year", "Rcv So Flag"], as_index=False
        )["Quantity[Unit1]"].sum()
        chart_df_bar = chart_df_bar.sort_values("Year")
    else:
        chart_df_bar = df_filtered.groupby(
            ["Period", "Rcv So Flag"], as_index=False
        )["Quantity[Unit1]"].sum()
        chart_df_bar = chart_df_bar.sort_values("Period")

    # --- Bar Chart ---
    fig_bar = px.bar(
        chart_df_bar,
        x="Year" if selected_year == "ALL" else "Period",
        y="Quantity[Unit1]",
        color="Rcv So Flag",
        barmode="group",
        title="📊 Inventory by " + ("Year" if selected_year == "ALL" else "Period and Category")
    )
    fig_bar.update_layout(
        xaxis_title="Year" if selected_year == "ALL" else "Period",
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
