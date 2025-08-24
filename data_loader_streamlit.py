import streamlit as st
import pandas as pd
import time

def load_data(filename="customer_raw_data.xlsx"):
    progress = st.progress(0, text="Starting...")

    # Step 1: Read Excel
    progress.progress(20, text="Reading Excel file...")
    df = pd.read_excel(filename)
    time.sleep(0.3)

    # Step 2: Clean Year / Month
    progress.progress(50, text="Processing Year/Month...")
    df["Year"] = df["Year"].astype(int).astype(str)
    df["Month"] = df["Month"].astype(int).astype(str).str.zfill(2)
    time.sleep(0.3)

    # Step 3: Create Period column
    progress.progress(80, text="Creating Period column...")
    df["Period"] = pd.to_datetime(df["Year"] + "-" + df["Month"], format="%Y-%m")
    time.sleep(0.3)

    st.session_state["official_data"] = df
    st.session_state["selected_site"] = df["Site"].dropna().unique()[0]

    progress.progress(100, text="✅ Done!")
    return df
