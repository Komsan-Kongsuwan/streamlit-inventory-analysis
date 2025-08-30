import streamlit as st
from streamlit_js_eval import streamlit_js_eval

# --- Load Bootstrap CSS ---
st.markdown("""
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css">
""", unsafe_allow_html=True)

# --- Render Bootstrap buttons ---
st.markdown("""
<div class="p-3">
    <form id="theme-form">
        <div class="mb-2">เลือก Theme:</div>
        <div class="btn-group" role="group">
            <input type="radio" name="theme" id="r1" value="Default" class="btn-check">
            <label for="r1" class="btn btn-outline-primary">Default</label>
        </div>
        <div class="btn-group" role="group">
            <input type="radio" name="theme" id="r2" value="Light" class="btn-check">
            <label for="r2" class="btn btn-outline-primary">Light</label>
        </div>
        <div class="btn-group" role="group">
            <input type="radio" name="theme" id="r3" value="Dark" class="btn-check">
            <label for="r3" class="btn btn-outline-primary">Dark</label>
        </div>                        
    </form>
    <input type="hidden" id="theme-value" value="">
</div>

<script>
document.querySelectorAll("input[name='theme']").forEach(radio => {
    radio.addEventListener("change", function() {
        document.getElementById("theme-value").value = this.value;
        window.dispatchEvent(new Event("themeChanged")); // force update
    });
});
</script>
""", unsafe_allow_html=True)

# --- Read hidden input value using JS ---
theme = streamlit_js_eval(
    js_expressions="document.getElementById('theme-value').value",
    key="theme_eval"
)

if theme:
    st.session_state["theme"] = theme

st.write("🎨 Current theme:", st.session_state.get("theme", "None"))
