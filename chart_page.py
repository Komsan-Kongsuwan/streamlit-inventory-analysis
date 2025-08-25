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

    # --- Button layout parameters ---
    total_buttons = len(years_list) + 1  # including "All"
    buttons_per_row = 8
    num_rows = math.ceil(total_buttons / buttons_per_row)
    left_width = min(total_buttons, buttons_per_row) * 2
    right_width = 20 - left_width
    right_width = max(right_width, 1)
    left_col, right_col = st.columns([left_width, right_width])

    # --- Generate clickable HTML buttons ---
    with left_col:
        btn_idx = 0
        for row in range(num_rows):
            cols_in_row = min(buttons_per_row, total_buttons - btn_idx)
            cols = st.columns(cols_in_row, gap="small")
            for c in range(cols_in_row):
                if btn_idx == 0:
                    year_label = "All"
                    selected = st.session_state.selected_year == "ALL"
                else:
                    year_label = str(years_list[btn_idx - 1])
                    selected = st.session_state.selected_year == years_list[btn_idx - 1]

                # Button color
                bg_color = "#4CAF50" if selected else "#E0E0E0"
                text_color = "#FFFFFF" if selected else "#000000"

                # HTML button with JS to update Streamlit session
                button_html = f"""
                <button onclick="
                    const streamlitEvent = new CustomEvent('streamlit:setComponentValue', {{
                        detail: '{year_label}'
                    }}); window.dispatchEvent(streamlitEvent);
                " style='width:100%; padding:6px 12px; margin-bottom:4px; border:none; border-radius:6px;
                        background-color:{bg_color}; color:{text_color}; cursor:pointer;'>{year_label}</button>
                """

                # Use st.markdown to render HTML button
                selected_value = cols[c].markdown(button_html, unsafe_allow_html=True)

                # Update session_state when button clicked via st.text_input workaround
                key = f"_hidden_input_{btn_idx}"
                if key not in st.session_state:
                    st.session_state[key] = year_label
                if st.session_state[key] != st.session_state.selected_year:
                    st.session_state.selected_year = st.session_state[key]

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

    # --- Keep only Rcv(increase) ---
    df_filtered = df_filtered[df_filtered["Rcv So Flag"] == "Rcv(increase)"]

    if df_filtered.empty:
        st.warning("⚠️ No data after filtering.")
        return

    df_filtered['Quantity[Unit1]'] = df_filtered['Quantity[Unit1]'].abs()

    # --- Aggregate by Period ---
    chart_df = df_filtered.groupby(["Period"], as_index=False)["Quantity[Unit1]"].sum()

    # --- Line Chart ---
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
