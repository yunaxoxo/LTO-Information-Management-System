from pathlib import Path
import streamlit as st

def css_style(style):
    try:
        current_dir = Path(__file__).parent
        css_path = current_dir.parent / "css" / style
        with open(css_path, "r") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
            
    except FileNotFoundError:
        st.error(f"Couldn't find CSS file at: {css_path}")

css_style("style.css")

st.title("Driver Registry")
st.markdown("Manage and monitor driver information, including licenses, violations, and other details.")
st.markdown("---")

LICENSE_TYPES = ["All Types", "Student", "Non-Professional", "Professional"]
TYPE_OPTIONS = [t for t in LICENSE_TYPES if t != "All Types"]
STATUS_OPTIONS = ["Valid", "Expired","Suspended", "Revoked"]

with st.sidebar: 
    st.header("Filter Drivers")
    license_type = st.selectbox("License Type", LICENSE_TYPES)
    status = st.multiselect("License Status", STATUS_OPTIONS, default= ["Valid"])   
    age_range = st.slider("Age Range", 16, 100, (16, 100))
    sex_filter = st.radio ("Sex", ["All", "Male", "Female"], horizontal=True)
    st.button("Apply Filters", use_container_width=True)

    st.markdown("---")
    st.markdown("Generate Report")
    if st.button("Expired / Suspended Licenses", use_container_width=True):
        st.session_state["show_expired_report"] = True