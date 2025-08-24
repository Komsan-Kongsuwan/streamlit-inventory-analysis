import streamlit as st
from data_loader import render_data_loader
from chart_page import render_chart_page

st.set_page_config(page_title="Inventory Analysis", layout="wide")

# Sidebar navigation
page = st.sidebar.radio("📌 Select Page", ["Data Loader", "Charts"])

if page == "Data Loader":
    render_data_loader()
elif page == "Charts":
    render_chart_page()
