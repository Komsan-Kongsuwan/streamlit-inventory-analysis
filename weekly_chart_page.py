import streamlit as st
import pandas as pd
import plotly.express as px

def render_weekly_page():
    st.title("📊 Weekly Inventory Flow")

    if "official_data" not in st.session_state:
        st.warning("⚠️ No data found. Please upload files in the Data Loader page first.")
        return

    df_raw = st.session_state["official_data"].copy()

    # --- Sidebar filters ---
    st.sidebar.subheader("🔍 Filters")

    # Year filter
    years_list = sorted(df_raw["Year"].dropna().unique())
    selected_year = st.sidebar.selectbox("Select Year", options=["ALL"] + years_list, index=0)

    # Item Code filter
    items = st.sidebar.multiselect("Select Item Code", options=df_raw["Item Code"].unique())

    # --- Apply filters ---
    df_filtered = df_raw.copy()
    if selected_year != "ALL":
        df_filtered = df_filtered[df_filtered["Year"] == selected_year]
    if items:
        df_filtered = df_filtered[df_filtered["Item Code"].isin(items)]

    if df_filtered.empty:
        st.warning("⚠️ No data after filtering.")
        return

    # --- Ensure date column is datetime ---
    df_filtered['Operation Date'] = pd.to_datetime(df_filtered['Operation Date'], errors='coerce')

    # Drop rows with invalid dates
    df_filtered = df_filtered.dropna(subset=['Operation Date'])

    # --- Create Week column (ISO week) ---
    df_filtered['Week'] = df_filtered['Operation Date'].dt.isocalendar().week

    # --- Keep only relevant categories ---
    df_filtered = df_filtered[df_filtered["Rcv So Flag"].isin(["Rcv(increase)", "So(decrese)"])]
    df_filtered['Quantity[Unit1]'] = df_filtered['Quantity[Unit1]'].abs()

    # --- Aggregate by Week + Category ---
    chart_df = df_filtered.groupby(["Week", "Rcv So Flag"], as_index=False)["Quantity[Unit1]"].sum()
    chart_df = chart_df.sort_values("Week")

    # --- Bar Chart ---
    fig_bar = px.bar(
        chart_df,
        x="Week",
        y="Quantity[Unit1]",
        color="Rcv So Flag",
        barmode="group",
        title=f"📊 Weekly Inventory Flow ({selected_year})" if selected_year != "ALL" else "📊 Weekly Inventory Flow (All Years)"
    )
    fig_bar.update_layout(
        xaxis_title="Week",
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

    st.plotly_chart(fig_bar, use_container_width=True)
