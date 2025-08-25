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

    # --- Sidebar filters ---
    years_list = sorted(df_raw["Year"].dropna().unique())
    selected_year = st.sidebar.selectbox("Select Year", ["ALL"] + list(years_list), index=0)

    months = list(range(1, 13))
    selected_month = st.sidebar.radio(
        "Select Month (optional)",
        ["All"] + [calendar.month_abbr[m] for m in months],
        index=0
    )
    selected_month_num = list(calendar.month_abbr).index(selected_month) if selected_month != "All" else None

    category_option = st.sidebar.radio(
        "Select Category",
        ["All", "Rcv(increase)", "So(decrese)"]
    )
    if category_option == "All":
        category_filter = ["Rcv(increase)", "So(decrese)"]
    else:
        category_filter = [category_option]

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
    if category_filter:
        df_filtered = df_filtered[df_filtered["Rcv So Flag"].isin(category_filter)]

    if df_filtered.empty:
        st.warning("⚠️ No data after filtering.")
        return

    df_filtered['Quantity[Unit1]'] = df_filtered['Quantity[Unit1]'].abs()

    # --- Determine aggregation ---
    if selected_month_num:
        # Daily aggregation
        if "Day" not in df_filtered.columns and "Operation Date" in df_filtered.columns:
            df_filtered["Day"] = pd.to_datetime(df_filtered["Operation Date"]).dt.day
        elif "Day" not in df_filtered.columns:
            df_filtered["Day"] = 1  # fallback
        x_col = "Day"
        all_days = pd.DataFrame({"Day": list(range(1,32))})
        chart_df = df_filtered.groupby([x_col, "Rcv So Flag"], as_index=False)["Quantity[Unit1]"].sum()
        chart_df = all_days.merge(chart_df, on="Day", how="left").fillna(0)
        chart_df["DayLabel"] = chart_df["Day"].astype(str) + "th"
        chart_df_wide = chart_df.pivot(index="DayLabel", columns="Rcv So Flag", values="Quantity[Unit1]").fillna(0).reset_index()
        y_cols = chart_df_wide.columns[1:]
        chart_title = f"📊 Daily Inventory in {selected_year}-{calendar.month_abbr[selected_month_num]}"
        x_col = "DayLabel"
    elif selected_year != "ALL":
        # Monthly aggregation
        x_col = "Month"
        all_months = pd.DataFrame({"Month": list(range(1,13))})
        chart_df = df_filtered.groupby([x_col, "Rcv So Flag"], as_index=False)["Quantity[Unit1]"].sum()
        chart_df = all_months.merge(chart_df, on="Month", how="left").fillna(0)
        chart_df["MonthLabel"] = chart_df["Month"].apply(lambda m: calendar.month_abbr[m])
        chart_df_wide = chart_df.pivot(index="MonthLabel", columns="Rcv So Flag", values="Quantity[Unit1]").fillna(0).reset_index()
        y_cols = chart_df_wide.columns[1:]
        chart_title = f"📊 Monthly Inventory in {selected_year}"
        x_col = "MonthLabel"
    else:
        # Yearly aggregation
        x_col = "Year"
        chart_df = df_filtered.groupby([x_col, "Rcv So Flag"], as_index=False)["Quantity[Unit1]"].sum()
        chart_df_wide = chart_df.pivot(index="Year", columns="Rcv So Flag", values="Quantity[Unit1]").fillna(0).reset_index()
        y_cols = chart_df_wide.columns[1:]
        chart_title = "📊 Inventory by Year"

    # --- Bar chart ---
    fig_bar = px.bar(
        chart_df_wide,
        x=x_col,
        y=y_cols,
        barmode="group",
        title=chart_title
    )
    fig_bar.update_layout(
        xaxis_title=x_col,
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
