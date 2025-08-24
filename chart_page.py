import streamlit as st
import pandas as pd
import plotly.express as px

def render_chart_page():
    st.title("📊 Inventory Flow by Operation Date")

    if "official_data" not in st.session_state:
        st.warning("⚠️ No data found. Please upload files in the Data Loader page first.")
        return

    df_raw = st.session_state["official_data"].copy()
    years_list = sorted(df_raw["Year"].dropna().unique())

    if "selected_year" not in st.session_state:
        st.session_state.selected_year = "ALL"

    # --- CSS for inline buttons ---
    st.markdown("""
        <style>
        .year-container {
            display: flex;
            flex-wrap: wrap;
            gap: 6px;   /* reduce spacing between buttons */
        }
        .year-container button {
            padding: 4px 10px;
            border-radius: 6px;
            border: 1px solid #ccc;
            background: #f9f9f9;
            cursor: pointer;
        }
        .year-container button.active {
            background: #0366d6;
            color: white;
            font-weight: bold;
        }
        </style>
    """, unsafe_allow_html=True)

    # --- Render inline buttons ---
    st.write("🔍 **Select Year**")
    year_html = '<div class="year-container">'
    year_html += f'<button class="{"active" if st.session_state.selected_year=="ALL" else ""}" onclick="window.location.href=\'?year=ALL\'">ALL</button>'
    for yr in years_list:
        year_html += f'<button class="{"active" if st.session_state.selected_year==yr else ""}" onclick="window.location.href=\'?year={yr}\'">{yr}</button>'
    year_html += '</div>'
    st.markdown(year_html, unsafe_allow_html=True)

    # --- Capture selection from query params ---
    query_params = st.query_params
    if "year" in query_params:
        st.session_state.selected_year = query_params["year"]
        if st.session_state.selected_year != "ALL":
            st.session_state.selected_year = int(st.session_state.selected_year)

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

    chart_df = (
        df_filtered.groupby(["Period"], as_index=False)["Quantity[Unit1]"]
        .sum()
    )

    fig = px.line(
        chart_df,
        x="Period",
        y="Quantity[Unit1]",
        markers=True,
        title="📈 Inventory Flow Over Time"
        if selected_year == "ALL"
        else f"📈 Inventory Flow Over Time ({selected_year})"
    )

    st.plotly_chart(fig, use_container_width=True)
