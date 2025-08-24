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

    st.write("🔍 **Select Year**")

    # --- Custom CSS to shrink gap ---
    st.markdown(
        """
        <style>
        div.button-row button {
            margin-right: 0.2rem !important;
            padding: 0.25rem 0.75rem;
        }
        div.button-row {
            display: flex;
            flex-wrap: wrap;
            gap: 2px;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    # --- Render year buttons in a form (real st.button) ---
    with st.form("year_selector"):
        cols_html = '<div class="button-row">'
        # add ALL
        cols_html += f'<button type="submit" name="year" value="ALL">ALL</button>'
        # add years
        for yr in years_list:
            cols_html += f'<button type="submit" name="year" value="{yr}">{yr}</button>'
        cols_html += "</div>"
        st.markdown(cols_html, unsafe_allow_html=True)

        selected_year = st.form_submit_button("")

    # --- Capture selection ---
    query_params = st.experimental_get_query_params()
    if "year" in query_params:
        st.session_state.selected_year = query_params["year"][0]

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
