import streamlit as st
from streamlit_js_eval import streamlit_js_eval

st.markdown("""
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css">
<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>

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

    <script>
    document.querySelectorAll("input[name='theme']").forEach(radio => {
        radio.addEventListener("change", function() {
            const theme = this.value;
            window.parent.postMessage({isStreamlitMessage: true, type: "themeChanged", theme: theme}, "*");
        });
    });
    </script>
</div>
""", unsafe_allow_html=True)

# Listen to JS event
theme = streamlit_js_eval(js_expressions="window.theme", key="theme-listener")

if theme:
    st.session_state["theme"] = theme

# Show result
st.write("🎨 Current theme:", st.session_state.get("theme", "None"))
