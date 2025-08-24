import streamlit as st
import pandas as pd
import plotly.express as px
from data_loader_streamlit import load_data
from excel_formatter import ExcelFormatter

def render_chart_page():
    # --- CSS ---
    st.markdown("""
        <style>
            .block-container {padding-top:1rem; padding-left:0.5rem; padding-right:0.5rem;}
        </style>
    """, unsafe_allow_html=True)

    # --- Load Data ---
    if "official_data" not in st.session_state:
        load_data("customer_raw_data.xlsx")

    df_raw = st.session_state["official_data"].copy()
    df_raw["Amount"] = pd.to_numeric(df_raw["Amount"], errors="coerce").fillna(0)

    # --- Sidebar : Customer filter ---
    customers = sorted(df_raw["Customer"].dropna().unique())
    selected_customers = st.sidebar.multiselect("Select Customer", customers, default=customers[:1])

    if not selected_customers:
        st.warning("⚠️ Please select at least one customer")
        st.stop()

    df_filtered = df_raw[df_raw["Customer"].isin(selected_customers)]

    # --- Main Filters (7 buttons) ---
    st.subheader("📊 Select Report")
    btns = [
        "daily stock", "daily receive and ship", "monthly receive ship",
        "weekly receive ship", "yearly receive ship", "stock aging", "storage day"
    ]
    selected_btn = st.radio("Select Report Type", btns, horizontal=True)

    st.markdown(f"### Showing report: **{selected_btn}**")

    # Example chart (replace with your real logic later)
    if selected_btn == "monthly receive ship":
        chart_df = df_filtered.groupby(["Period"], as_index=False)["Amount"].sum()
        fig = px.line(chart_df, x="Period", y="Amount", markers=True, title="Monthly Receive/Ship")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info(f"⚠️ Report type '{selected_btn}' not implemented yet.")

    # --- Download Excel ---
    formatter = ExcelFormatter(df_filtered, "customer_report.xlsx")
    excel_file = formatter.save_to_excel({"FilteredData": df_filtered})

    st.download_button(
        label="📥 Download Excel Report",
        data=excel_file,
        file_name="customer_report.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
