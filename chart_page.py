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
    years_list_str = [str(y) for y in years_list]

    # Initialize session state for selected_year
    if "selected_year" not in st.session_state:
        st.session_state.selected_year = "ALL"

    # Radio buttons for year selection
    selected_year = st.radio(
        "Select Year",
        options=["ALL"] + years_list_str,
        index=(0 if st.session_state.selected_year == "ALL"
               else years_list_str.index(str(st.session_state.selected_year))),
        horizontal=True
    )

    # Update session state only if changed
    if selected_year != st.session_state.selected_year:
        st.session_state.selected_year = selected_year

    st.write(f"✅ Selected Year: **{st.session_state.selected_year}**" 
             if st.session_state.selected_year != "ALL" 
             else "✅ Showing data for **All Years**")

    # --- Item filter ---
    items = st.multiselect("Item Code", df_raw["Item Code"].unique())

    # --- Apply filters ---
    df_filtered = df_raw.copy()
    if st.session_state.selected_year != "ALL":
        df_filtered = df_filtered[df_filtered["Year"] == int(st.session_state.selected_year)]
    if items:
        df_filtered = df_filtered[df_filtered["Item Code"].isin(items)]

    df_filtered = df_filtered[df_filtered["Rcv So Flag"] == "Rcv(increase)"]

    if df_filtered.empty:
        st.warning("⚠️ No data after filtering.")
        return

    df_filtered['Quantity[Unit1]'] = df_filtered['Quantity[Unit1]'].abs()

    chart_df = df_filtered.groupby(["Period"], as_index=False)["Quantity[Unit1]"].sum()

    fig = px.line(
        chart_df,
        x="Period",
        y="Quantity[Unit1]",
        markers=True,
        title="📈 Inventory Flow Over Time"
        if st.session_state.selected_year=="ALL"
        else f"📈 Inventory Flow Over Time ({st.session_state.selected_year})"
    )

    fig.update_layout(
        xaxis_title="Period",
        yaxis_title="Quantity",
        template="plotly_white"
    )

    st.plotly_chart(fig, use_container_width=True)
