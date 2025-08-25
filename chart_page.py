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

    # --- Dynamic column ratio ---
    left_width = min(total_buttons, buttons_per_row) * 2  # 2 units per button
    right_width = 30 - left_width
    right_width = max(right_width, 1)  # prevent zero width

    left_col, right_col = st.columns([left_width, right_width])

    with left_col:
        btn_idx = 0
        for row in range(num_rows):
            cols_in_row = min(buttons_per_row, total_buttons - btn_idx)
            cols = st.columns(cols_in_row, gap="small")
            for c in range(cols_in_row):
                if btn_idx == 0:
                    # "All" button
                    if cols[c].button("✅ All"):
                        st.session_state.selected_year = "ALL"
                else:
                    yr = years_list[btn_idx - 1]
                    if cols[c].button(str(yr)):
                        st.session_state.selected_year = yr
                btn_idx += 1

    selected_year = st.session_state.selected_year
    if selected_year == "ALL":
        st.write("✅ Showing data for **All Years**")
    else:
        st.write(f"✅ Selected Year: **{selected_year}**")

    # --- Item filter ---
    items = st.multiselect("Item Code", df_raw["Item Code"].unique())

    # --- Apply filters ---
    df_filtered = df_raw.copy()
    if selected_year != "ALL":
        df_filtered = df_filtered[df_filtered["Year"] == selected_year]
    if items:
        df_filtered = df_filtered[df_filtered["Item Code"].isin(items)]





    

    if df_filtered.empty:
        st.warning("⚠️ No data after filtering.")
        return




      # --- Take absolute values for Quantity[Unit1] ---
    df_filtered['Quantity[Unit1]'] = df_filtered['Quantity[Unit1]'].abs()
    
    # --- Apply aggregation depending on selection ---
    if selected_year == "ALL":
        # ✅ Line chart by Period
        chart_df_line = df_filtered.groupby(["Period", "Rcv So Flag"], as_index=False)["Quantity[Unit1]"].sum()
    
        # ✅ Bar chart by Year
        chart_df_bar = df_filtered.groupby(["Year", "Rcv So Flag"], as_index=False)["Quantity[Unit1]"].sum()
    else:
        # ✅ Both charts by Period
        chart_df_line = df_filtered.groupby(["Period", "Rcv So Flag"], as_index=False)["Quantity[Unit1]"].sum()
        chart_df_bar = chart_df_line.copy()
    
    # --- Line Chart (Period only, no legend) ---
    fig_line = px.line(
        chart_df_line,
        x="Period",
        y="Quantity[Unit1]",
        color="Rcv So Flag",
        markers=True,
        title="📈 Inventory Flow Over Time"
        if selected_year == "ALL"
        else f"📈 Inventory Flow Over Time ({selected_year})"
    )
    fig_line.update_layout(
        xaxis_title="Period",
        yaxis_title="Quantity",
        template="plotly_white",
        showlegend=False
    )
    
    # --- Bar Chart (Year if ALL, else Period, legend bottom) ---
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
    
    # --- Display side by side (60:40) ---
    col1, col2 = st.columns([60, 40])
    with col1:
        st.plotly_chart(fig_line, use_container_width=True)
    with col2:
        st.plotly_chart(fig_bar, use_container_width=True)
