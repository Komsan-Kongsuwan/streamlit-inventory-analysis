import streamlit as st
from chart_page import render_chart_page

st.set_page_config(
    page_title="📊 Monthly Revenue Dashboard",
    layout="wide"
)

# run chart page immediately
render_chart_page()
