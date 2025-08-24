# streamlit_monthly

import streamlit as st
import pandas as pd
import numpy as np
import calendar
from openpyxl import load_workbook
from openpyxl.styles import Alignment
from openpyxl.utils import get_column_letter
import io

st.set_page_config(page_title="Inventory Analysis (Admin)", layout="wide")
st.title("💹 Inventory Analysis")

# ✅ Uploader
uploaded_files = st.file_uploader("📤 Upload .xlsx files", type="xlsx", accept_multiple_files=True)

if not uploaded_files:
    st.info("Please upload one or more monthly Excel files (e.g. 202401.xlsx).")
    st.stop()

st.success("✅ Files uploaded. If you want to upload again, please move to another page and back to this page again to reset the uploaded files. Otherwise, uploaded files will be duplicated!")

def generate_official_report(files):
    try:
        df_list = []
        progress_bar = st.progress(0)

        for i, file in enumerate(files):
            progress_bar.progress(int((i + 1) / len(files) * 100))
            filename = file.name

            # Read Excel with only specific columns
            df = pd.read_excel(
                file,
                skiprows=2,          # skip first 2 rows if headers are on 3rd row
                nrows=49,            # limit rows if needed
                usecols=[
                    "Operation Date", "Rcv So Flag", "Owner Code", "Owner Name",
                    "Item Code", "Item Name", "Quantity[Unit1]", "UOM1",
                    "Inventory Qty", "Delivery Destination Code", "Delivery Destination Name"
                ]
            )

            # Extract Year/Month from filename (assuming format YYYYMM.xlsx)
            year = filename[0:4]
            month = filename[4:6]
            df["Year"] = year
            df["Month"] = month

            df_list.append(df)

        if not df_list:
            st.warning("⚠️ No valid data found in uploaded files.")
            return pd.DataFrame(), pd.DataFrame()

        df_final = pd.concat(df_list, ignore_index=True)
        df_final['Quantity[Unit1]'] = pd.to_numeric(df_final['Quantity[Unit1]'], errors='coerce').fillna(0)

        # --- pivot table ---
        pivot_df = pd.pivot_table(
            df_final,
            index=['Owner Code', 'Owner Name', 'Item Code', 'Item Name', 'Year'],
            columns='Month',
            values='Quantity[Unit1]',
            aggfunc='sum',
            fill_value=0,
            observed=False
        )
        pivot_df['Grand Total'] = pivot_df.sum(axis=1)
        pivot_df = pivot_df.reset_index()

        # Rename month columns from 01..12 to Jan..Dec
        month_map = {f"{i:02d}": calendar.month_abbr[i] for i in range(1, 13)}
        pivot_df = pivot_df.rename(columns=month_map)

        final_columns = (
            ['Owner Code', 'Owner Name', 'Item Code', 'Item Name', 'Year']
            + list(month_map.values())
            + ['Grand Total']
        )
        pivot_df = pivot_df.reindex(columns=final_columns)

        return pivot_df, df_final

    except Exception as e:
        st.warning("⚠️ Error while processing files. Please upload correct files again.")
        st.caption(f"Details: {e}")
        return pd.DataFrame(), pd.DataFrame()

# --- Main execution ---
df_pivot, df_raw = generate_official_report(uploaded_files)

if df_raw.empty:
    st.warning("⚠️ You uploaded wrong files, Please upload files again (Browse files).")
    st.stop()

st.dataframe(df_raw)

# 👉 Save to session for Chart page
st.session_state["official_data"] = df_raw
