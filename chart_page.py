# chart_page.py
import streamlit as st
import plotly.express as px
import pandas as pd
from data_loader_streamlit import DataLoaderStreamlit

def render_chart_page():
    st.markdown("""
        <style>
            .block-container {
                padding-top: 1rem;
                padding-left: 0.5rem;
                padding-right: 0.5rem;
                padding-bottom: 0rem;
            }
            div[data-testid="stHorizontalBlock"] > div {
                flex: 1;
                margin: 0 5px;
            }
            .filter-btn {
                display: inline-block;
                margin: 6px;
            }
        </style>
    """, unsafe_allow_html=True)

    # --- Load data via DataLoaderStreamlit ---
    loader = DataLoaderStreamlit()
    loader.run()
    df = loader.df  # ข้อมูลหลักที่โหลดมาแล้ว
    if df is None or df.empty:
        st.warning("⚠️ No data available.")
        return

    # --- Sidebar filter (Customer) ---
    customers = sorted(df["Customer"].dropna().unique())
    selected_customers = st.sidebar.multiselect(
        "Select Customer(s)",
        customers,
        default=customers[:1] if customers else []
    )

    if not selected_customers:
        st.info("Please select at least one customer.")
        return

    df_filtered = df[df["Customer"].isin(selected_customers)]

    # --- Main Filter Buttons ---
    st.subheader("📊 Data Visualization")
    filter_options = [
        "daily stock",
        "daily receive and ship",
        "monthly receive ship",
        "weekly receive ship",
        "yearly receive ship",
        "stock aging",
        "storage day",
    ]

    selected_filter = st.radio(
        "Select Data View",
        filter_options,
        horizontal=True
    )

    # --- Display Graphs Based on Filter ---
    if selected_filter == "daily stock":
        st.write("📦 Daily Stock")
        daily_df = df_filtered.groupby("Date", as_index=False)["Stock"].sum()
        fig = px.line(daily_df, x="Date", y="Stock", title="Daily Stock")
        st.plotly_chart(fig, use_container_width=True)

    elif selected_filter == "daily receive and ship":
        st.write("📥📤 Daily Receive & Ship")
        daily_rs = df_filtered.groupby("Date", as_index=False)[["Receive", "Ship"]].sum()
        fig = px.bar(daily_rs, x="Date", y=["Receive", "Ship"], barmode="group")
        st.plotly_chart(fig, use_container_width=True)

    elif selected_filter == "monthly receive ship":
        st.write("📥📤 Monthly Receive & Ship")
        monthly = df_filtered.groupby("Month", as_index=False)[["Receive", "Ship"]].sum()
        fig = px.line(monthly, x="Month", y=["Receive", "Ship"], markers=True)
        st.plotly_chart(fig, use_container_width=True)

    elif selected_filter == "weekly receive ship":
        st.write("📥📤 Weekly Receive & Ship")
        weekly = df_filtered.groupby("Week", as_index=False)[["Receive", "Ship"]].sum()
        fig = px.line(weekly, x="Week", y=["Receive", "Ship"], markers=True)
        st.plotly_chart(fig, use_container_width=True)

    elif selected_filter == "yearly receive ship":
        st.write("📥📤 Yearly Receive & Ship")
        yearly = df_filtered.groupby("Year", as_index=False)[["Receive", "Ship"]].sum()
        fig = px.bar(yearly, x="Year", y=["Receive", "Ship"], barmode="group")
        st.plotly_chart(fig, use_container_width=True)

    elif selected_filter == "stock aging":
        st.write("⏳ Stock Aging")
        if "AgingDays" in df_filtered.columns:
            fig = px.histogram(df_filtered, x="AgingDays", nbins=20, title="Stock Aging (days)")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No `AgingDays` column found in dataset.")

    elif selected_filter == "storage day":
        st.write("🏭 Storage Day")
        if "StorageDays" in df_filtered.columns:
            storage = df_filtered.groupby("Customer", as_index=False)["StorageDays"].mean()
            fig = px.bar(storage, x="Customer", y="StorageDays", title="Average Storage Days")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No `StorageDays` column found in dataset.")

    # --- Add download button ---
    loader.render_download_button()


# Run immediately when page opened
if __name__ == "__main__":
    render_chart_page()
