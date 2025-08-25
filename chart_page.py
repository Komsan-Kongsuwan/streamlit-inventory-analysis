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
    selected_year = st.sidebar.selectbox("Select Year", ["ALL"] + list(years_list), index=0)

    # --- Sidebar: Month filter (vertical buttons) ---
    month_names = list(calendar.month_abbr)[1:]  # Jan ... Dec
    selected_month = st.sidebar.radio("Select Month (optional)", ["All"] + month_names, index=0)
    if selected_month != "All":
        selected_month_num = month_names.index(selected_month) + 1
    else:
        selected_month_num = None

    # --- Sidebar: Rcv/So category filter ---
    cat_option = st.sidebar.radio(
        "Select Category",
        ["All", "Rcv increase", "So decrese"],
        index=0
    )
    if cat_option == "All":
        categories = ["Rcv(increase)", "So(decrese)"]
    elif cat_option == "Rcv increase":
        categories = ["Rcv(increase)"]
    else:
        categories = ["So(decrese)"]

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
    df_filtered = df_filtered[df_filtered["Rcv So Flag"].isin(categories)]
    df_filtered['Quantity[Unit1]'] = df_filtered['Quantity[Unit1]'].abs()

    if df_filtered.empty:
        st.warning("⚠️ No data after filtering.")
        return

    # --- Determine aggregation level ---
    if selected_month_num:
        # Daily aggregation
        if "Day" not in df_filtered.columns and "Operation Date" in df_filtered.columns:
            df_filtered["Day"] = pd.to_datetime(df_filtered["Operation Date"]).dt.day
        elif "Day" not in df_filtered.columns:
            df_filtered["Day"] = 1  # fallback
        x_col = "Day"
        # Fill missing days
        all_days = pd.DataFrame({ "Day": list(range(1, 32)) })
        chart_df = df_filtered.groupby([x_col, "Rcv So Flag"], as_index=False)["Quantity[Unit1]"].sum()
        chart_df = all_days.merge(chart_df, on="Day", how="left")
        chart_df["Quantity[Unit1]"] = chart_df["Quantity[Unit1]"].fillna(0)
        chart_title = f"📊 Daily Inventory in {selected_year}-{selected_month}"
    elif selected_year != "ALL":
        # Monthly aggregation
        x_col = "Month"
        all_months = pd.DataFrame({"Month": list(range(1,13))})
        chart_df = df_filtered.groupby([x_col, "Rcv So Flag"], as_index=False)["Quantity[Unit1]"].sum()
        chart_df = all_months.merge(chart_df, on="Month", how="left")
        chart_df["Quantity[Unit1]"] = chart_df["Quantity[Unit1]"].fillna(0)
        chart_df[x_col] = chart_df[x_col].apply(lambda m: calendar.month_abbr[m])
        chart_title = f"📊 Monthly Inventory in {selected_year}"
    else:
        # Yearly aggregation
        x_col = "Year"
        chart_df = df_filtered.groupby([x_col, "Rcv So Flag"], as_index=False)["Quantity[Unit1]"].sum()
        chart_title = "📊 Inventory by Year"

    # --- Pivot table to wide format ---
    if x_col in ["Month", "Day"]:
        chart_df_wide = chart_df.pivot_table(
            index=x_col,
            columns="Rcv So Flag",
            values="Quantity[Unit1]",
            fill_value=0
        ).reset_index()
        y_cols = [col for col in chart_df_wide.columns if col != x_col]
    else:
        chart_df_wide = chart_df
        y_cols = ["Quantity[Unit1]"]

    # --- Plot bar chart ---
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
