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
    
    # --- Aggregate differently for ALL vs single year ---
    if selected_year == "ALL":
        chart_df = df_filtered.groupby(["Year", "Rcv So Flag"], as_index=False)["Quantity[Unit1]"].sum()
        x_col = "Year"
    else:
        chart_df = df_filtered.groupby(["Period", "Rcv So Flag"], as_index=False)["Quantity[Unit1]"].sum()
        x_col = "Period"
    
    # --- Line Chart (2 categories, no legend) ---
    fig_line = px.line(
        chart_df,
        x=x_col,
        y="Quantity[Unit1]",
        color="Rcv So Flag",
        markers=True,
        title="📈 Inventory Flow Over Time"
        if selected_year == "ALL"
        else f"📈 Inventory Flow Over Time ({selected_year})"
    )
    fig_line.update_layout(
        xaxis_title=x_col,
        yaxis_title="Quantity",
        template="plotly_white",
        showlegend=False   # 🔹 Hide legend
    )
    
    # --- Bar Chart (legend at bottom) ---
    fig_bar = px.bar(
        chart_df,
        x=x_col,
        y="Quantity[Unit1]",
        color="Rcv So Flag",
        barmode="group",
        title="📊 Inventory by " + x_col + " and Category"
    )
    fig_bar.update_layout(
        xaxis_title=x_col,
        yaxis_title="Quantity",
        template="plotly_white",
        legend=dict(
            orientation="h",        # 🔹 horizontal
            yanchor="bottom",
            y=-0.3,                 # 🔹 move below chart
            xanchor="center",
            x=0.5
        )
    )
