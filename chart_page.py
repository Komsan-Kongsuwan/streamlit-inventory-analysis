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
    st.subheader("🔍 Filters")

    # --- Year buttons ---
    years_list = sorted(df_raw["Year"].dropna().unique())
    if "selected_year" not in st.session_state:
        st.session_state.selected_year = "ALL"

    total_buttons = len(years_list) + 1  # +1 for "All"
    buttons_per_row = 8  # max buttons per row
    num_rows = math.ceil(total_buttons / buttons_per_row)

    # --- Dynamic column ratio for buttons ---
    left_width = min(total_buttons, buttons_per_row) * 2
    right_width = 30 - left_width
    right_width = max(right_width, 1)

    left_col, right_col = st.columns([left_width, right_width])
    with left_col:
        btn_idx = 0
        for row in range(num_rows):
            cols_in_row = min(buttons_per_row, total_buttons - btn_idx)
            cols = st.columns(cols_in_row, gap="small")
            for c in range(cols_in_row):
                if btn_idx == 0 and cols[c].button("✅ All"):
                    st.session_state.selected_year = "ALL"
                elif btn_idx > 0:
                    yr = years_list[btn_idx - 1]
                    if cols[c].button(str(yr)):
                        st.session_state.selected_year = yr
                btn_idx += 1

    selected_year = st.session_state.selected_year
    st.write(f"✅ Selected Year: **{selected_year}**" if selected_year != "ALL" else "✅ Showing data for **All Years**")

    # --- Item filter ---
    items = st.multiselect("Item Code", df_raw["Item Code"].unique())

    # --- Filter data ---
    df_filtered = df_raw.copy()
    if selected_year != "ALL":
        df_filtered = df_filtered[df_filtered["Year"] == selected_year]
    if items:
        df_filtered = df_filtered[df_filtered["Item Code"].isin(items)]

    # --- Keep only "Rcv(increase)" ---
    df_filtered = df_filtered[df_filtered["Rcv So Flag"] == "Rcv(increase)"]

    if df_filtered.empty:
        st.warning("⚠️ No data after filtering.")
        return

    # --- Ensure Period is int ---
    df_filtered['Period'] = pd.to_numeric(df_filtered['Period'], errors='coerce')
    df_filtered = df_filtered.dropna(subset=['Period'])
    df_filtered['Period'] = df_filtered['Period'].astype(int)

    # --- Absolute quantity ---
    df_filtered['Quantity[Unit1]'] = df_filtered['Quantity[Unit1]'].abs()

    # --- Aggregation ---
    if selected_year == "ALL":
        # Line chart by Period
        chart_df_line = df_filtered.groupby(["Period", "Rcv So Flag"], as_index=False)["Quantity[Unit1]"].sum()
        chart_df_line = chart_df_line.sort_values("Period")
        # Bar chart by Year
        chart_df_bar = df_filtered.groupby(["Year", "Rcv So Flag"], as_index=False)["Quantity[Unit1]"].sum()
        chart_df_bar = chart_df_bar.sort_values("Year")
    else:
        chart_df_line = df_filtered.groupby(["Period", "Rcv So Flag"], as_index=False)["Quantity[Unit1]"].sum()
        chart_df_line = chart_df_line.sort_values("Period")
        chart_df_bar = chart_df_line.copy()  # Bar chart uses Period

    # --- Line Chart ---
    if not chart_df_line.empty:
        fig_line = px.line(
            chart_df_line,
            x="Period",
            y="Quantity[Unit1]",
            color="Rcv So Flag",
            markers=True,
            title=f"📈 Inventory Flow Over Time ({selected_year})" if selected_year != "ALL" else "📈 Inventory Flow Over Time"
        )
        fig_line.update_layout(xaxis_title="Period", yaxis_title="Quantity", template="plotly_white", showlegend=False)
    else:
        fig_line = None

    # --- Bar Chart ---
    if not chart_df_bar.empty:
        x_col = "Year" if selected_year == "ALL" else "Period"
        fig_bar = px.bar(
            chart_df_bar,
            x=x_col,
            y="Quantity[Unit1]",
            color="Rcv So Flag",
            barmode="group",
            title="📊 Inventory by " + ("Year" if selected_year == "ALL" else "Period and Category")
        )
        fig_bar.update_layout(
            xaxis_title=x_col,
            yaxis_title="Quantity",
            template="plotly_white",
            legend=dict(orientation="h", yanchor="bottom", y=-0.3, xanchor="center", x=0.5)
        )
    else:
        fig_bar = None

    # --- Display side by side (60:40) ---
    col1, col2 = st.columns([60, 40])
    if fig_line:
        with col1:
            st.plotly_chart(fig_line, use_container_width=True)
    if fig_bar:
        with col2:
            st.plotly_chart(fig_bar, use_container_width=True)




    # --- Display side by side (60:40) ---
    col1, col2 = st.columns([60, 40])
    with col1:
        st.plotly_chart(fig_line, use_container_width=True)
    with col2:
        st.plotly_chart(fig_bar, use_container_width=True)
