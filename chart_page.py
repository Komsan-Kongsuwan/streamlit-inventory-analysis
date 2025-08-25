import streamlit as st
import pandas as pd
import plotly.express as px
import math

def render_chart_page():
    st.title("📊 Inventory Flow Quick Preview")

    if "official_data" not in st.session_state:
        st.warning("⚠️ No data found. Please upload files in the Data Loader page first.")
        return

    df_raw = st.session_state["official_data"].copy()
    df_raw['Operation Date'] = pd.to_datetime(df_raw['Operation Date'], errors='coerce')
    df_raw = df_raw.dropna(subset=['Operation Date'])

    st.sidebar.subheader("🔍 Filters")

    # --- Year filter in sidebar ---
    years_list = sorted(df_raw["Year"].dropna().unique())
    selected_year = st.sidebar.selectbox("Select Year", options=["ALL"] + years_list, index=0)

    # --- Filter by selected year ---
    df_filtered = df_raw.copy()
    if selected_year != "ALL":
        df_filtered = df_filtered[df_filtered["Year"] == selected_year]

    if df_filtered.empty:
        st.warning("⚠️ No data after filtering.")
        return

    # --- Month filter as buttons in main page ---
    months_list = sorted(df_filtered["Operation Date"].dt.month.unique())
    st.subheader("Select Month")
    month_buttons = st.columns(len(months_list))
    selected_month = None
    for i, m in enumerate(months_list):
        if month_buttons[i].button(str(m)):
            selected_month = m

    if selected_month:
        df_filtered = df_filtered[df_filtered["Operation Date"].dt.month == selected_month]

    if df_filtered.empty:
        st.warning("⚠️ No data for selected month.")
        return

    # --- Item filter in main page ---
    items = st.multiselect("Select Item Code", options=df_filtered["Item Code"].unique())
    if items:
        df_filtered = df_filtered[df_filtered["Item Code"].isin(items)]

    if df_filtered.empty:
        st.warning("⚠️ No data after item filter.")
        return

    # --- Keep only relevant categories ---
    df_filtered = df_filtered[df_filtered["Rcv So Flag"].isin(["Rcv(increase)", "So(decrese)"])]
    df_filtered['Quantity[Unit1]'] = df_filtered['Quantity[Unit1]'].abs()

    # --- Aggregate by day ---
    df_filtered["Day"] = df_filtered["Operation Date"].dt.day
    chart_df = df_filtered.groupby(["Day", "Rcv So Flag"], as_index=False)["Quantity[Unit1]"].sum()
    chart_df = chart_df.sort_values("Day")

    # --- Daily Bar Chart ---
    fig_bar = px.bar(
        chart_df,
        x="Day",
        y="Quantity[Unit1]",
        color="Rcv So Flag",
        barmode="group",
        title=f"📊 Daily Inventory in {selected_year}-{str(selected_month).zfill(2)}"
    )
    fig_bar.update_layout(
        xaxis_title="Day",
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


"""
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
    df_raw['Operation Date'] = pd.to_datetime(df_raw['Operation Date'], errors='coerce')
    df_raw = df_raw.dropna(subset=['Operation Date'])

    st.sidebar.subheader("🔍 Filters")

    # --- Year selection ---
    years_list = sorted(df_raw["Year"].dropna().unique())
    selected_year = st.sidebar.selectbox("Select Year", options=["ALL"] + years_list, index=0)

    # --- Month selection (only if a specific year is selected) ---
    if selected_year != "ALL":
        df_year = df_raw[df_raw["Year"] == selected_year]
        months_list = sorted(df_year["Operation Date"].dt.month.unique())
        selected_month = st.sidebar.selectbox("Select Month", options=["ALL"] + months_list, index=0)
    else:
        selected_month = "ALL"

    # --- Item filter ---
    items = st.sidebar.multiselect("Select Item Code", options=df_raw["Item Code"].unique())

    # --- Apply filters ---
    df_filtered = df_raw.copy()
    if selected_year != "ALL":
        df_filtered = df_filtered[df_filtered["Year"] == selected_year]
    if selected_month != "ALL":
        df_filtered = df_filtered[df_filtered["Operation Date"].dt.month == selected_month]
    if items:
        df_filtered = df_filtered[df_filtered["Item Code"].isin(items)]

    if df_filtered.empty:
        st.warning("⚠️ No data after filtering.")
        return

    # --- Keep only relevant categories ---
    df_filtered = df_filtered[df_filtered["Rcv So Flag"].isin(["Rcv(increase)", "So(decrese)"])]
    df_filtered['Quantity[Unit1]'] = df_filtered['Quantity[Unit1]'].abs()

    # --- Determine aggregation level ---
    if selected_year == "ALL":
        # Sum per Year + Rcv flag
        chart_df = df_filtered.groupby(["Year", "Rcv So Flag"], as_index=False)["Quantity[Unit1]"].sum()
        x_col = "Year"
        chart_title = "📊 Inventory Flow by Year"
    elif selected_month == "ALL":
        # Sum per Month + Rcv flag
        df_filtered["Month"] = df_filtered["Operation Date"].dt.month
        chart_df = df_filtered.groupby(["Month", "Rcv So Flag"], as_index=False)["Quantity[Unit1]"].sum()
        x_col = "Month"
        chart_title = f"📊 Inventory Flow in {selected_year} by Month"
    else:
        # Sum per Day + Rcv flag
        df_filtered["Day"] = df_filtered["Operation Date"].dt.day
        chart_df = df_filtered.groupby(["Day", "Rcv So Flag"], as_index=False)["Quantity[Unit1]"].sum()
        x_col = "Day"
        chart_title = f"📊 Inventory Flow in {selected_year}-{str(selected_month).zfill(2)} by Day"

    chart_df = chart_df.sort_values(x_col)

    # --- Bar chart ---
    fig_bar = px.bar(
        chart_df,
        x=x_col,
        y="Quantity[Unit1]",
        color="Rcv So Flag",
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
    """



"""
import streamlit as st
import pandas as pd
import plotly.express as px

def render_chart_page():
    st.title("📊 Inventory Flow by Operation Date")

    if "official_data" not in st.session_state:
        st.warning("⚠️ No data found. Please upload files in the Data Loader page first.")
        return

    df_raw = st.session_state["official_data"].copy()

    # --- Sidebar Year filter ---
    years_list = sorted(df_raw["Year"].dropna().unique())
    selected_year = st.sidebar.radio(
        "Select Year",
        options=["ALL"] + years_list,
        index=0
    )

    # --- Item filter in main page ---
    items = st.multiselect("Item Code", df_raw["Item Code"].unique())

    st.write(
        f"✅ Showing data for **{selected_year}**"
        if selected_year != "ALL"
        else "✅ Showing data for **All Years**"
    )

    # --- Apply filters ---
    df_filtered = df_raw.copy()
    if selected_year != "ALL":
        df_filtered = df_filtered[df_filtered["Year"] == selected_year]
    if items:
        df_filtered = df_filtered[df_filtered["Item Code"].isin(items)]

    if df_filtered.empty:
        st.warning("⚠️ No data after filtering.")
        return

    # --- Keep only relevant categories ---
    df_filtered = df_filtered[df_filtered["Rcv So Flag"].isin(["Rcv(increase)", "So(decrese)"])]
    df_filtered['Quantity[Unit1]'] = df_filtered['Quantity[Unit1]'].abs()

    # --- Aggregate for bar chart ---
    if selected_year == "ALL":
        chart_df_bar = df_filtered.groupby(
            ["Year", "Rcv So Flag"], as_index=False
        )["Quantity[Unit1]"].sum()
        chart_df_bar = chart_df_bar.sort_values("Year")
    else:
        chart_df_bar = df_filtered.groupby(
            ["Period", "Rcv So Flag"], as_index=False
        )["Quantity[Unit1]"].sum()
        chart_df_bar = chart_df_bar.sort_values("Period")

    # --- Bar Chart ---
    fig_bar = px.bar(
        chart_df_bar,
        x="Year" if selected_year == "ALL" else "Period",
        y="Quantity[Unit1]",
        color="Rcv So Flag",
        barmode="group",
        title="📊 Inventory by " + ("Year" if selected_year == "ALL" else "Period and Category")
    )
    fig_bar.update_layout(
        xaxis_title="Year" if selected_year == "ALL" else "Period",
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
    """
