import streamlit as st
import pandas as pd
import plotly.express as px
import math

def render_chart_page():
    st.title("📊 Inventory Flow by Operation Date")

    if "official_data" not in st.session_state:
        st.warning("⚠️ No data found. Please upload files in the Data Loader page first.")
        return

    df_raw = st.session_state["official_data"].copy()

    # --- Ensure Month and Week exist ---
    if "Operation Date" in df_raw.columns:
        df_raw["Operation Date"] = pd.to_datetime(df_raw["Operation Date"], errors="coerce")
        df_raw["Month"] = df_raw["Operation Date"].dt.month
        df_raw["Week"] = df_raw["Operation Date"].dt.isocalendar().week.astype(int)

    # --- Sidebar Filters ---
    st.sidebar.subheader("🔍 Filters")

    # Year buttons
    years_list = sorted(df_raw["Year"].dropna().unique())
    if "selected_year" not in st.session_state:
        st.session_state.selected_year = "ALL"

    total_buttons = len(years_list) + 1
    buttons_per_row = 4  # Sidebar narrower
    num_rows = math.ceil(total_buttons / buttons_per_row)

    st.sidebar.write("### Select Year")
    btn_idx = 0
    for row in range(num_rows):
        cols_in_row = min(buttons_per_row, total_buttons - btn_idx)
        cols = st.sidebar.columns(cols_in_row, gap="small")
        for c in range(cols_in_row):
            if btn_idx == 0:
                if cols[c].button("✅ All"):
                    st.session_state.selected_year = "ALL"
            else:
                yr = years_list[btn_idx - 1]
                if cols[c].button(str(yr)):
                    st.session_state.selected_year = yr
            btn_idx += 1

    selected_year = st.session_state.selected_year

    # Item, Month, Week filters
    items = st.sidebar.multiselect("Item Code", df_raw["Item Code"].unique())
    months = st.sidebar.multiselect("Month", sorted(df_raw["Month"].dropna().unique()))
    weeks = st.sidebar.multiselect("Week", sorted(df_raw["Week"].dropna().unique()))

    st.write(f"✅ Showing data for **{selected_year}**" if selected_year != "ALL" else "✅ Showing data for **All Years**")

    # --- Apply filters ---
    df_filtered = df_raw.copy()
    if selected_year != "ALL":
        df_filtered = df_filtered[df_filtered["Year"] == selected_year]
    if items:
        df_filtered = df_filtered[df_filtered["Item Code"].isin(items)]
    if months:
        df_filtered = df_filtered[df_filtered["Month"].isin(months)]
    if weeks:
        df_filtered = df_filtered[df_filtered["Week"].isin(weeks)]

    if df_filtered.empty:
        st.warning("⚠️ No data after filtering.")
        return

    # --- Keep only relevant Rcv So Flag categories ---
    df_filtered = df_filtered[df_filtered["Rcv So Flag"].isin(["Rcv(increase)", "So(decrese)"])]

    # --- Take absolute values for Quantity ---
    df_filtered['Quantity[Unit1]'] = df_filtered['Quantity[Unit1]'].abs()

    # --- Aggregate correctly to avoid double-counting ---
    if selected_year == "ALL":
        chart_df_bar = df_filtered.groupby(["Year", "Rcv So Flag"], as_index=False)["Quantity[Unit1]"].sum()
        chart_df_bar = chart_df_bar.sort_values("Year")
    else:
        chart_df_bar = df_filtered.groupby(["Period", "Rcv So Flag"], as_index=False)["Quantity[Unit1]"].sum()
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
