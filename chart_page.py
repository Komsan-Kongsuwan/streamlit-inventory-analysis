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

    years_list = sorted(df_raw["Year"].dropna().unique())

    if "selected_year" not in st.session_state:
        st.session_state.selected_year = "ALL"

    # --- Wrap year buttons into multiple rows ---
    buttons_per_row = 6  # adjust as needed
    total_buttons = len(years_list) + 1  # +1 for "All" button
    num_rows = math.ceil(total_buttons / buttons_per_row)

    # Flatten list of buttons for layout
    btn_idx = 0
    for row in range(num_rows):
        # Create columns for this row
        cols_in_row = min(buttons_per_row, total_buttons - btn_idx)
        cols = st.columns(cols_in_row, gap="small")

        # Fill each column with button
        for c in range(cols_in_row):
            if btn_idx == 0:
                # First button is "All"
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

    df_filtered = df_filtered[df_filtered["Rcv So Flag"] == "Rcv(increase)"]

    if df_filtered.empty:
        st.warning("⚠️ No data after filtering.")
        return

    df_filtered['Quantity[Unit1]'] = df_filtered['Quantity[Unit1]'].abs()

    chart_df = df_filtered.groupby(["Period"], as_index=False)["Quantity[Unit1]"].sum()

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
        xaxis_title="Operation Date",
        yaxis_title="Quantity",
        template="plotly_white"
    )

    st.plotly_chart(fig, use_container_width=True)
