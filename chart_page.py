import streamlit as st
import pandas as pd
import plotly.express as px
import calendar

def render_chart_page():
    st.title("📊 Inventory Flow by Operation Date")

    if "official_data" not in st.session_state:
        st.warning("⚠️ No data found. Please upload files in the Data Loader page first.")
        return

    df_raw = st.session_state["official_data"].copy()

    # --- Sidebar: Year filter ---
    years_list = sorted(df_raw["Year"].dropna().unique())
    selected_year = st.sidebar.selectbox(
        "Select Year", ["ALL"] + list(years_list), index=0
    )

    # --- Sidebar: Month filter (vertical buttons) ---
    months = list(range(1, 13))
    selected_month = st.sidebar.radio(
        "Select Month (optional)",
        ["All"] + [calendar.month_abbr[m] for m in months],
        index=0
    )
    if selected_month != "All":
        selected_month_num = list(calendar.month_abbr).index(selected_month)
    else:
        selected_month_num = None

    # --- Sidebar: Category filter ---
    category_option = st.sidebar.selectbox(
        "Select Category",
        [
            "All (Rcv increase & So decrese)",
            "Rcv increase only",
            "So decrese only"
        ],
        index=0
    )

    # --- Main page: Item filter ---
    items = st.multiselect("Item Code", df_raw["Item Code"].unique())

    # --- Apply filters ---
    df_filtered = df_raw.copy()
    if selected_year != "ALL":
        df_filtered = df_filtered[df_filtered["Year"] == selected_year]
    if selected_month_num:
        df_filtered = df_filtered[df_filtered["Month"] == selected_month_num]
    if items:
        df_filtered = df_filtered[df_filtered["Item Code"].isin(items)]

    # --- Apply Category filter ---
    if category_option == "Rcv increase only":
        df_filtered = df_filtered[df_filtered["Rcv So Flag"] == "Rcv(increase)"]
    elif category_option == "So decrese only":
        df_filtered = df_filtered[df_filtered["Rcv So Flag"] == "So(decrese)"]

    if df_filtered.empty:
        st.warning("⚠️ No data after filtering.")
        return

    # --- Keep relevant categories and absolute values ---
    df_filtered['Quantity[Unit1]'] = df_filtered['Quantity[Unit1]'].abs()

    # --- Determine aggregation level and fill missing months/days ---
    if selected_month_num:
        # Daily aggregation
        if "Day" not in df_filtered.columns and "Operation Date" in df_filtered.columns:
            df_filtered["Day"] = pd.to_datetime(df_filtered["Operation Date"]).dt.day
        elif "Day" not in df_filtered.columns:
            df_filtered["Day"] = 1

        # Group by Day and Rcv So Flag
        chart_df = df_filtered.groupby(["Day", "Rcv So Flag"], as_index=False)["Quantity[Unit1]"].sum()

        # Fill missing days
        all_days = pd.DataFrame({"Day": list(range(1, 32))})
        chart_df = (
            pd.merge(all_days.assign(key=1), chart_df.assign(key=1), on="key", how="left")
            .drop("key", axis=1)
        )
        chart_df["Quantity[Unit1]"] = chart_df["Quantity[Unit1]"].fillna(0)
        chart_df["Rcv So Flag"] = chart_df["Rcv So Flag"].fillna("No Data")

        x_col = "Day"
        x_labels = [f"{d}" for d in range(1, 32)]
        chart_title = f"📊 Daily Inventory in {selected_year}-{calendar.month_abbr[selected_month_num]}"
    elif selected_year != "ALL":
        # Monthly aggregation
        chart_df = df_filtered.groupby(["Month", "Rcv So Flag"], as_index=False)["Quantity[Unit1]"].sum()

        # Fill missing months
        all_months = pd.DataFrame({"Month": list(range(1, 13))})
        chart_df = (
            pd.merge(all_months.assign(key=1), chart_df.assign(key=1), on="key", how="left")
            .drop("key", axis=1)
        )
        chart_df["Quantity[Unit1]"] = chart_df["Quantity[Unit1]"].fillna(0)
        chart_df["Rcv So Flag"] = chart_df["Rcv So Flag"].fillna("No Data")

        x_col = "Month"
        x_labels = [calendar.month_abbr[m] for m in range(1, 13)]
        chart_title = f"📊 Monthly Inventory in {selected_year}"
    else:
        # Yearly aggregation
        chart_df = df_filtered.groupby(["Year", "Rcv So Flag"], as_index=False)["Quantity[Unit1]"].sum()
        x_col = "Year"
        x_labels = chart_df["Year"].astype(str).tolist()
        chart_title = "📊 Inventory by Year"

    # --- Bar chart ---
    fig_bar = px.bar(
        chart_df,
        x=x_col,
        y="Quantity[Unit1]",
        color="Rcv So Flag",
        barmode="group",
        title=chart_title
    )

    # --- Set custom x-axis labels ---
    if x_col == "Month":
        fig_bar.update_layout(xaxis=dict(tickmode="array", tickvals=list(range(1, 13)), ticktext=x_labels))
    elif x_col == "Day":
        fig_bar.update_layout(xaxis=dict(tickmode="array", tickvals=list(range(1, 32)), ticktext=x_labels))

    fig_bar.update_layout(
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
