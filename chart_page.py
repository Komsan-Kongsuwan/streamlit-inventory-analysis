import streamlit as st
import pandas as pd
import plotly.express as px
import calendar

def render_chart_page():
    st.title("📊 Inventory Flow Quick Preview")

    if "official_data" not in st.session_state:
        st.warning("⚠️ No data found. Please upload files in the Data Loader page first.")
        return

    df_raw = st.session_state["official_data"].copy()
    df_raw['Operation Date'] = pd.to_datetime(df_raw['Operation Date'], errors='coerce')
    df_raw = df_raw.dropna(subset=['Operation Date'])

    st.sidebar.subheader("🔍 Filters")

    # --- Year filter in sidebar ---
    years_list = sorted(df_raw["Year"].dropna().unique())
    selected_year = st.sidebar.selectbox("Select Year", options=["ALL"] + years_list, index=0)

    # --- Filter by selected year ---
    df_filtered = df_raw.copy()
    if selected_year != "ALL":
        df_filtered = df_filtered[df_filtered["Year"] == selected_year]

    if df_filtered.empty:
        st.warning("⚠️ No data after filtering.")
        return

    # --- Month filter as buttons with abbreviated month names ---
    months_list = sorted(df_filtered["Operation Date"].dt.month.unique())
    st.subheader("Select Month")
    month_buttons = st.columns(len(months_list))
    selected_month = None
    for i, m in enumerate(months_list):
        month_abbr = calendar.month_abbr[m]  # Abbreviated month name
        if month_buttons[i].button(month_abbr):
            selected_month = m

    if selected_month:
        df_filtered = df_filtered[df_filtered["Operation Date"].dt.month == selected_month]

    if df_filtered.empty:
        st.warning("⚠️ No data for selected month.")
        return

    # --- Item filter in main page ---
    items = st.multiselect("Select Item Code", options=df_filtered["Item Code"].unique())
    if items:
        df_filtered = df_filtered[df_filtered["Item Code"].isin(items)]

    if df_filtered.empty:
        st.warning("⚠️ No data after item filter.")
        return

    # --- Keep only relevant categories ---
    df_filtered = df_filtered[df_filtered["Rcv So Flag"].isin(["Rcv(increase)", "So(decrese)"])]
    df_filtered['Quantity[Unit1]'] = df_filtered['Quantity[Unit1]'].abs()

    # --- Aggregate by day ---
    df_filtered["Day"] = df_filtered["Operation Date"].dt.day
    chart_df = df_filtered.groupby(["Day", "Rcv So Flag"], as_index=False)["Quantity[Unit1]"].sum()
    chart_df = chart_df.sort_values("Day")

    # --- Daily Bar Chart ---
    fig_bar = px.bar(
        chart_df,
        x="Day",
        y="Quantity[Unit1]",
        color="Rcv So Flag",
        barmode="group",
        title=f"📊 Daily Inventory in {selected_year}-{calendar.month_abbr[selected_month]}"
    )
    fig_bar.update_layout(
        xaxis_title="Day",
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
