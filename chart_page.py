import streamlit as st
import pandas as pd
import plotly.express as px
import calendar

def render_chart_page():
    st.title("📊 Inventory Flow by Operation Date")

    if "official_data" not in st.session_state:
        st.warning("⚠️ No data found. Please upload files in the Data Loader page first.")
        return

    df_raw = st.session_state["official_data"].copy()

    # ---------------- Sidebar Filters ----------------
    st.sidebar.subheader("🔍 Filters")

    # --- Year filter ---
    years_list = sorted(df_raw["Year"].dropna().unique())
    selected_year = st.sidebar.selectbox("Select Year", ["ALL"] + list(years_list), index=0)
    st.sidebar.session_state.selected_year = selected_year

    # --- Month filter (vertical buttons) ---
    selected_month = None
    st.sidebar.markdown("### Select Month")
    for m in range(1, 13):
        if st.sidebar.button(calendar.month_abbr[m]):
            selected_month = m
            st.session_state.selected_month = selected_month
    # Use session_state if no button clicked yet
    if "selected_month" in st.session_state and selected_month is None:
        selected_month = st.session_state.selected_month

    # ---------------- Main body filters ----------------
    items = st.multiselect("Item Code", df_raw["Item Code"].unique())

    # ---------------- Apply filters ----------------
    df_filtered = df_raw.copy()
    if selected_year != "ALL":
        df_filtered = df_filtered[df_filtered["Year"] == selected_year]
    if selected_month is not None:
        df_filtered = df_filtered[df_filtered["Month"] == selected_month]
    if items:
        df_filtered = df_filtered[df_filtered["Item Code"].isin(items)]

    if df_filtered.empty:
        st.warning("⚠️ No data after filtering.")
        return

    # Keep only relevant categories
    df_filtered = df_filtered[df_filtered["Rcv So Flag"].isin(["Rcv(increase)", "So(decrese)"])]
    df_filtered['Quantity[Unit1]'] = df_filtered['Quantity[Unit1]'].abs()

    # ---------------- Aggregate chart ----------------
    if selected_month is not None:
        # Daily chart in selected month
        chart_df = df_filtered.groupby(["Day", "Rcv So Flag"], as_index=False)["Quantity[Unit1]"].sum()
        x_col = "Day"
        chart_title = f"📊 Daily Inventory in {selected_year}-{calendar.month_abbr[selected_month]}"
    elif selected_year != "ALL":
        # Monthly chart in selected year
        chart_df = df_filtered.groupby(["Month", "Rcv So Flag"], as_index=False)["Quantity[Unit1]"].sum()
        x_col = "Month"
        chart_title = f"📊 Monthly Inventory in {selected_year}"
        # Replace month number with abbreviated month names
        chart_df[x_col] = chart_df[x_col].apply(lambda x: calendar.month_abbr[x])
    else:
        # Yearly chart
        chart_df = df_filtered.groupby(["Year", "Rcv So Flag"], as_index=False)["Quantity[Unit1]"].sum()
        x_col = "Year"
        chart_title = "📊 Inventory by Year"

    # ---------------- Bar chart ----------------
    fig_bar = px.bar(
        chart_df,
        x=x_col,
        y="Quantity[Unit1]",
        color="Rcv So Flag",
        barmode="group",
        title=chart_title
    )
    fig_bar.update_layout(
        xaxis_title=x_col,
        yaxis_title="Quantity",
        template="plotly_white",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.25,
            xanchor="center",
            x=0.5
        )
    )

    st.plotly_chart(fig_bar, use_container_width=True)
