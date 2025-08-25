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

    total_buttons = len(years_list) + 1  # +1 for "All"
    buttons_per_row = 8
    num_rows = math.ceil(total_buttons / buttons_per_row)

    # Dynamic left/right column ratio
    left_width = min(total_buttons, buttons_per_row) * 2
    right_width = 20 - left_width
    right_width = max(right_width, 1)

    left_col, right_col = st.columns([left_width, right_width])

    with left_col:
        btn_idx = 0
        for row in range(num_rows):
            cols_in_row = min(buttons_per_row, total_buttons - btn_idx)
            cols = st.columns(cols_in_row, gap="small")
            for c in range(cols_in_row):
                # Determine label and background color
                if btn_idx == 0:
                    year_label = "All"
                    is_selected = st.session_state.selected_year == "ALL"
                else:
                    year_label = str(years_list[btn_idx - 1])
                    is_selected = st.session_state.selected_year == years_list[btn_idx - 1]

                bg_color = "#4CAF50" if is_selected else "#E0E0E0"  # green if selected, light gray if not
                text_color = "#FFFFFF" if is_selected else "#000000"

                # Create HTML button
                button_html = f"""
                <div style='text-align:center; margin-bottom:4px'>
                    <button style='background-color:{bg_color}; color:{text_color};
                                   border:none; padding:6px 12px; border-radius:6px; width:100%; cursor:pointer;'>
                        {year_label}
                    </button>
                </div>
                """

                if cols[c].button(year_label) or st.markdown(button_html, unsafe_allow_html=True):
                    if btn_idx == 0:
                        st.session_state.selected_year = "ALL"
                    else:
                        st.session_state.selected_year = years_list[btn_idx - 1]

                btn_idx += 1

    selected_year = st.session_state.selected_year
    if selected_year == "ALL":
        st.write("✅ Showing data for **All Years**")
    else:
        st.write(f"✅ Selected Year: **{selected_year}**")

    # Item filter
    items = st.multiselect("Item Code", df_raw["Item Code"].unique())

    # Apply filters
    df_filtered = df_raw.copy()
    if selected_year != "ALL":
        df_filtered = df_filtered[df_filtered["Year"] == selected_year]
    if items:
        df_filtered = df_filtered[df_filtered["Item Code"].isin(items)]

    # Keep only Rcv(increase)
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
        xaxis_title="Period",
        yaxis_title="Quantity",
        template="plotly_white"
    )

    st.plotly_chart(fig, use_container_width=True)
