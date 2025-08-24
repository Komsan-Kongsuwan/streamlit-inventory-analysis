import streamlit as st
import pandas as pd
import calendar
import re

st.set_page_config(page_title="Inventory Analysis (Admin)", layout="wide")
st.title("💹 Inventory Analysis")

# ✅ Uploader
uploaded_files = st.file_uploader("📤 Upload .csv files", type="csv", accept_multiple_files=True)

if not uploaded_files:
    st.info("Please upload one or more monthly CSV files (e.g. 202401.csv).")
    st.stop()

st.success("✅ Files uploaded. If you want to upload again, please move to another page and back to this page again to reset the uploaded files. Otherwise, uploaded files will be duplicated!")

# --- Canonical columns we want ---
REQUIRED_COLS = [
    "Operation Date", "Rcv So Flag", "Owner Code", "Owner Name",
    "Item Code", "Item Name", "Quantity[Unit1]", "UOM1",
    "Inventory Qty", "Delivery Destination Code", "Delivery Destination Name"
]

# --- Normalization / rename map (normalized header -> canonical header) ---
def norm(s: str) -> str:
    s = str(s).replace("\ufeff", "")      # remove BOM
    s = re.sub(r"\s+", " ", s).strip()    # collapse spaces
    return s.lower()

NAME_MAP = {
    "operation date": "Operation Date",
    "rcv so flag": "Rcv So Flag",
    "owner code": "Owner Code",
    "owner name": "Owner Name",
    "item code": "Item Code",
    "item name": "Item Name",
    "quantity[unit1]": "Quantity[Unit1]",
    "uom1": "UOM1",
    "inventory qty": "Inventory Qty",
    "delivery destination code": "Delivery Destination Code",
    "delivery destination name": "Delivery Destination Name",
    # Optional tolerant aliases:
    "quantity [unit1]": "Quantity[Unit1]",
    "inventory quantity": "Inventory Qty",
    "delivery dest code": "Delivery Destination Code",
    "delivery dest name": "Delivery Destination Name",
}

def smart_read_csv(file) -> pd.DataFrame:
    """
    Read CSV with auto delimiter, normalize headers, and rename to canonical names.
    """
    df = pd.read_csv(
        file,
        sep=None,            # auto-detect delimiter
        engine="python",     # required for sep=None
        encoding="utf-8-sig",
        dtype=str            # read raw as strings first to avoid parse issues
    )

    # Normalize then rename to canonical
    renamed = {}
    for c in df.columns:
        nc = norm(c)
        renamed[c] = NAME_MAP.get(nc, re.sub(r"\s+", " ", str(c).replace("\ufeff","")).strip())
    df = df.rename(columns=renamed)

    return df

def generate_official_report(files):
    try:
        df_list = []
        progress_bar = st.progress(0)

        for i, file in enumerate(files):
            progress_bar.progress(int((i + 1) / len(files) * 100))
            filename = file.name

            df = smart_read_csv(file)

            # Check required columns and report helpful hints
            missing = [c for c in REQUIRED_COLS if c not in df.columns]
            if missing:
                st.warning(f"⚠️ Skipping `{filename}` because required columns are missing: {missing}")
                st.caption(f"Found columns: {list(df.columns)}")
                continue

            # Keep only the required columns
            df = df[REQUIRED_COLS].copy()

            # Parse date
            df["Operation Date"] = pd.to_datetime(
                df["Operation Date"], errors="coerce", dayfirst=True, infer_datetime_format=True
            )

            # Add Year/Month (fallback to filename if date missing)
            df["Year"] = df["Operation Date"].dt.year
            df["Month"] = df["Operation Date"].dt.month

            # If all Year/Month are NA, try pulling from filename like YYYYMM.csv
            if df["Year"].isna().all() or df["Month"].isna().all():
                m = re.search(r"(\d{4})(\d{2})", filename)
                if m:
                    y, mth = int(m.group(1)), int(m.group(2))
                    df["Year"] = df["Year"].fillna(y)
                    df["Month"] = df["Month"].fillna(mth)

            # Clean quantity
            df["Quantity[Unit1]"] = pd.to_numeric(df["Quantity[Unit1]"], errors="coerce").fillna(0)

            df_list.append(df)

        if not df_list:
            st.warning("⚠️ No valid data found in uploaded files.")
            return pd.DataFrame(), pd.DataFrame()

        df_final = pd.concat(df_list, ignore_index=True)

        # --- pivot table ---
        pivot_df = pd.pivot_table(
            df_final,
            index=['Owner Code', 'Owner Name', 'Item Code', 'Item Name', 'Year'],
            columns='Month',
            values='Quantity[Unit1]',
            aggfunc='sum',
            fill_value=0,
            observed=False
        ).reset_index()

        # Add Grand Total
        month_cols = [c for c in pivot_df.columns if isinstance(c, (int, float))]
        pivot_df["Grand Total"] = pivot_df[month_cols].sum(axis=1)

        # Rename numeric months 1..12 → Jan..Dec
        month_map = {i: calendar.month_abbr[i] for i in range(1, 13)}
        pivot_df = pivot_df.rename(columns=month_map)

        final_columns = (
            ['Owner Code', 'Owner Name', 'Item Code', 'Item Name', 'Year']
            + list(calendar.month_abbr[1:])  # ['Jan', ..., 'Dec']
            + ['Grand Total']
        )
        # Reindex safely (keep only existing month columns)
        existing_final = [c for c in final_columns if c in pivot_df.columns]
        pivot_df = pivot_df.reindex(columns=existing_final)

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
st.session_state["official_data"] = df_raw
