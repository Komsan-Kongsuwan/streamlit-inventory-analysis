import streamlit as st
import pandas as pd
import calendar

st.set_page_config(page_title="Inventory Analysis", layout="wide")

def generate_official_report(files):
    try:
        df_list = []
        progress_bar = st.progress(0)

        for i, file in enumerate(files):
            progress_bar.progress(int((i + 1) / len(files) * 100))
            filename = file.name

            # ✅ Read CSV (auto-detect delimiter)
            df = pd.read_csv(
                file,
                sep=None,            # auto-detect delimiter
                engine="python",     # required for sep=None
                usecols=[
                    "Operation Date", "Rcv So Flag", "Owner Code", "Owner Name",
                    "Item Code", "Item Name", "Quantity[Unit1]", "UOM1",
                    "Inventory Qty", "Delivery Destination Code", "Delivery Destination Name"
                ]
            )

            # ✅ Convert Operation Date to datetime
            df["Operation Date"] = pd.to_datetime(df["Operation Date"], errors="coerce", dayfirst=True)

            # ✅ Add Year/Month columns/Period
            df["Period"] = df["Operation Date"].dt.to_period("M").astype(str)
            df["Year"] = df["Operation Date"].dt.year
            df["Month"] = df["Operation Date"].dt.month

            df_list.append(df)

        if not df_list:
            st.warning("⚠️ No valid data found in uploaded files.")
            return pd.DataFrame(), pd.DataFrame()

        df_final = pd.concat(df_list, ignore_index=True)
        df_final['Quantity[Unit1]'] = pd.to_numeric(df_final['Quantity[Unit1]'], errors='coerce').fillna(0)
        df_final['Quantity[Unit1]'] = df_final['Quantity[Unit1]'].abs()
        # --- pivot table ---
        pivot_df = pd.pivot_table(
            df_final,
            index=['Owner Code', 'Owner Name', 'Item Code', 'Item Name', 'Year', 'Rcv So Flag'],
            columns='Month',
            values='Quantity[Unit1]',
            aggfunc='sum',
            fill_value=0,
            observed=False
        )
        pivot_df['Grand Total'] = pivot_df.sum(axis=1)
        pivot_df = pivot_df.reset_index()

        # Rename month columns 1..12 → Jan..Dec
        month_map = {i: calendar.month_abbr[i] for i in range(1, 13)}
        pivot_df = pivot_df.rename(columns=month_map)

        final_columns = (
            ['Owner Code', 'Owner Name', 'Item Code', 'Item Name', 'Year', 'Rcv So Flag']
            + list(month_map.values())
            + ['Grand Total']
        )
        pivot_df = pivot_df.reindex(columns=final_columns)

        return pivot_df, df_final

    except Exception as e:
        st.warning("⚠️ Error while processing files. Please upload correct files again.")
        st.caption(f"Details: {e}")
        return pd.DataFrame(), pd.DataFrame()


def render_data_loader():
    st.title("💹 Inventory Analysis – Data Loader")

    # ✅ Uploader
    uploaded_files = st.file_uploader("📤 Upload .csv files", type="csv", accept_multiple_files=True)

    if not uploaded_files:
        st.info("Please upload one or more monthly CSV files (e.g. 202401.csv).")
        return

    st.success("✅ Files uploaded. If you want to upload again, please move to another page and back to this page again.")

    # --- Main execution ---
    df_pivot, df_raw = generate_official_report(uploaded_files)

    if df_raw.empty:
        st.warning("⚠️ You uploaded wrong files, Please upload files again.")
        return

    # 👉 Save to session for Chart page
    st.session_state["official_data"] = df_raw

    st.subheader("📊 Preview of Uploaded Data")
    st.dataframe(df_raw)
    
render_data_loader()
