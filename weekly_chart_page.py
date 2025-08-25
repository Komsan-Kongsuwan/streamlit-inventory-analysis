# weekly_page.py
import streamlit as st
import pandas as pd
import plotly.express as px

def render_weekly_page():
    st.title("📊 Inventory Flow by Week")

    if "official_data" not in st.session_state:
        st.warning("⚠️ No data found. Please upload files in the Data Loader page first.")
        return

    df_raw = st.session_state["official_data"].copy()

    # --- Sidebar filters ---
    st.sidebar.header("Filters")

    # --- Year filter ---
    years_list = sorted(df_raw["Year"].dropna().unique())
    selected_year = st.sidebar.selectbox("Select Year", ["ALL"] + years_list)

    # --- Week filter (only if year selected) ---
    if selected_year != "ALL":
        df_year = df_raw[df_raw["Year"] == selected_year]
        weeks_list = sorted(df_year["Week"].dropna().unique())
        selected_week = st.sidebar.multiselect("Select Week(s)", weeks_list, default=weeks_list)
    else:
        selected_week = []

    # --- Apply filters ---
    df_filtered = df_raw.copy()
    if selected_year != "ALL":
        df_filtered = df_filtered[df_filtered["Year"] == selected_year]
    if selected_week:
        df_filtered = df_filtered[df_filtered["Week"].isin(selected_week)]

    # --- Item filter ---
    items = st.sidebar.multiselect("Item Code", df_filtered["Item Code"].unique())
    if items:
        df_filtered = df_filtered[df_filtered["Item Code"].isin(items)]

    if df_filtered.empty:
        st.warning("⚠️ No data after filtering.")
        return

    # --- Keep only relevant Rcv So Flag categories ---
    df_filtered = df_filtered[df_filtered["Rcv So Flag"].isin(["Rcv(increase)", "So(decrese)"])]
    df_filtered['Quantity[Unit1]'] = df_filtered['Quantity[Unit1]'].abs()

    # --- Aggregate by Week ---
    chart_df = df_filtered.groupby(["Week", "Rcv So Flag"], as_index=False)["Quantity[Unit1]"].sum()
    chart_df = chart_df.sort_values("Week")

    # --- Bar Chart ---
    fig_bar = px.bar(
        chart_df,
        x="Week",
        y="Quantity[Unit1]",
        color="Rcv So Flag",
        barmode="group",
        title=f"📊 Inventory Flow by Week ({selected_year})" if selected_year != "ALL" else "📊 Inventory Flow by Week"
    )
    fig_bar.update_layout(
        xaxis_title="Week",
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
