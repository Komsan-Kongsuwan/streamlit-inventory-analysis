import streamlit as st
import pandas as pd
import plotly.express as px
import calendar

def day_suffix(d):
    if 11 <= d <= 13:
        return f"{d}th"
    last_digit = d % 10
    if last_digit == 1:
        return f"{d}st"
    elif last_digit == 2:
        return f"{d}nd"
    elif last_digit == 3:
        return f"{d}rd"
    else:
        return f"{d}th"

def render_chart_page():
    # --- Page CSS ---
    st.markdown("""
        <style>
            .block-container {padding: 1.5rem 1rem 0 1rem;}
            section[data-testid="stSidebar"] div.stButton > button {
                font-size: 12px !important; padding: 0.1rem 0.25rem !important;
                min-height: 40px !important; border-radius: 6px !important; line-height:1.2;
            }
            section[data-testid="stSidebar"] div.stButton p { font-size: 12px !important; margin:0 !important; }
            [data-testid="stMetric"] { padding: 0.25rem 0.5rem; min-height: 60px; margin:0 !important;}
            [data-testid="stMetricLabel"] { font-size: 14px !important; font-weight: 600 !important; color: #333333; }
            [data-testid="stMetricValue"] { font-size: 16px !important; font-weight: 700 !important; color: #0055aa; }
            div.block-container > div {margin-bottom: 0rem !important;}
        </style>
    """, unsafe_allow_html=True)

    # --- Page Title ---
    st.markdown("<h2 style='text-align:left; font-size:28px;'>📊 Receive-Ship Visualization (6)</h2>", unsafe_allow_html=True)

    if "official_data" not in st.session_state:
        st.warning("⚠️ No data found. Please upload files in the Data Loader page first.")
        return

    df_raw = st.session_state["official_data"].copy()

    # --- Sidebar filters ---
    years_list = sorted(df_raw["Year"].dropna().unique())
    selected_year = st.sidebar.selectbox("Select Year", ["ALL"] + list(years_list), index=0)

    months = list(range(1,13))
    selected_month = st.sidebar.radio("Select Month (optional)", ["All"] + [calendar.month_abbr[m] for m in months], index=0)
    selected_month_num = list(calendar.month_abbr).index(selected_month) if selected_month != "All" else None

    items = st.multiselect("Item Code", df_raw["Item Code"].unique())

    # --- Apply filters ---
    df_filtered = df_raw.copy()
    if selected_year != "ALL":
        df_filtered = df_filtered[df_filtered["Year"] == selected_year]
    if selected_month_num:
        df_filtered = df_filtered[df_filtered["Month"] == selected_month_num]
    if items:
        df_filtered = df_filtered[df_filtered["Item Code"].isin(items)]
    if df_filtered.empty:
        st.warning("⚠️ No data after filtering.")
        return

    df_filtered = df_filtered[df_filtered["Rcv So Flag"].isin(["Rcv(increase)", "So(decrese)"])]
    df_filtered['Quantity[Unit1]'] = df_filtered['Quantity[Unit1]'].abs()

    # ==========================================================
    # 📊 CHART
    # ==========================================================
    if selected_month_num:
        df_filtered["Day"] = pd.to_datetime(df_filtered["Operation Date"]).dt.day
        total_days = pd.Series(range(1,32))
        chart_df = df_filtered.groupby(["Day","Rcv So Flag"], as_index=False)["Quantity[Unit1]"].sum()
        all_days_flags = pd.MultiIndex.from_product([total_days, chart_df["Rcv So Flag"].unique()], names=["Day","Rcv So Flag"])
        chart_df = chart_df.set_index(["Day","Rcv So Flag"]).reindex(all_days_flags, fill_value=0).reset_index()
        chart_df["x_label"] = chart_df["Day"].apply(day_suffix)
        chart_title = f"📊 Daily Receive-Ship in {selected_year}-{calendar.month_abbr[selected_month_num]}"
    elif selected_year != "ALL":
        chart_df = df_filtered.groupby(["Month","Rcv So Flag"], as_index=False)["Quantity[Unit1]"].sum()
        all_months_flags = pd.MultiIndex.from_product([months, chart_df["Rcv So Flag"].unique()], names=["Month","Rcv So Flag"])
        chart_df = chart_df.set_index(["Month","Rcv So Flag"]).reindex(all_months_flags, fill_value=0).reset_index()
        chart_df["x_label"] = chart_df["Month"].apply(lambda m: calendar.month_abbr[m])
        chart_title = f"📊 Monthly Receive-Ship in {selected_year}"
    else:
        chart_df = df_filtered.groupby(["Year","Rcv So Flag"], as_index=False)["Quantity[Unit1]"].sum()
        chart_df["x_label"] = chart_df["Year"].astype(str)
        chart_title = "📊 Receive-Ship by Year"

    fig_bar = px.bar(
        chart_df,
        x="x_label",
        y="Quantity[Unit1]",
        color="Rcv So Flag",
        barmode="group",
        title=chart_title,
        height=400   # chart height
    )
    fig_bar.update_layout(
        xaxis_title="",
        yaxis_title="Quantity",
        template="plotly_white",
        legend=dict(orientation="h", yanchor="bottom", y=-0.3, xanchor="center", x=0.5),
        margin=dict(l=0, r=0, t=50, b=0),  # remove extra top/bottom margin
        legend_title_text=""  # 👈 remove legend title
    )
    
    
    st.plotly_chart(fig_bar, use_container_width=True)

    # ==========================================================
    # 📌 INFO BOXES
    # ==========================================================
    df_raw['YearMonth'] = df_raw['Year']*100 + df_raw['Month']
    last_12_months = sorted(df_raw['YearMonth'].unique())[-12:]
    df_last12 = df_raw[df_raw['YearMonth'].isin(last_12_months)]
    active_items = df_last12[df_last12["Rcv So Flag"].isin(["Rcv(increase)", "So(decrese)"])]["Item Code"].unique()
    total_item_codes = df_raw["Item Code"].nunique()
    movement_items = len(active_items)
    non_movement_items = total_item_codes - movement_items

    if selected_year != "ALL":
        prev_data = df_raw[df_raw["Year"] < selected_year]
        if selected_month_num:
            prev_data = pd.concat([prev_data, df_raw[(df_raw["Year"]==selected_year) & (df_raw["Month"]<selected_month_num)]])
        prev_items = set(prev_data["Item Code"].unique())
        new_item_codes = len(set(df_filtered["Item Code"].unique()) - prev_items)
    else:
        new_item_codes = 0

    day_rcv = df_filtered[df_filtered["Rcv So Flag"]=="Rcv(increase)"]["Operation Date"].dt.date.nunique()
    day_so  = df_filtered[df_filtered["Rcv So Flag"]=="So(decrese)"]["Operation Date"].dt.date.nunique()
    item_rcv = df_filtered[df_filtered["Rcv So Flag"]=="Rcv(increase)"]["Item Code"].nunique()
    item_so  = df_filtered[df_filtered["Rcv So Flag"]=="So(decrese)"]["Item Code"].nunique()
    amount_rcv = df_filtered[df_filtered["Rcv So Flag"]=="Rcv(increase)"]["Quantity[Unit1]"].sum()
    amount_so  = df_filtered[df_filtered["Rcv So Flag"]=="So(decrese)"]["Quantity[Unit1]"].sum()

    # --- Display compact info cards in one row at bottom ---
    cols = st.columns(9)
    with cols[0]: st.metric("Total Items", total_item_codes)
    with cols[1]: st.metric("Movement Items", movement_items)
    with cols[2]: st.metric("Non-Movement", non_movement_items)
    with cols[3]: st.metric("New Items", new_item_codes)
    with cols[4]: st.metric("Receive (Day)", day_rcv)
    with cols[5]: st.metric("Ship (Day)", day_so)
    with cols[6]: st.metric("Receive (Item)", item_rcv)
    with cols[7]: st.metric("Ship (Item)", item_so)
    with cols[8]: st.metric("QTY Receive/Ship", f"{amount_rcv:.0f}/{amount_so:.0f}")
