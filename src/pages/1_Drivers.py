from pathlib import Path
import pandas as pd
import streamlit as st
from controllers import driver_controller as dc

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

# Define filter options
LICENSE_TYPES = ["All Types", "Student", "Non-Professional", "Professional"]
TYPE_OPTIONS = [t for t in LICENSE_TYPES if t != "All Types"]
STATUS_OPTIONS = ["Valid", "Expired","Suspended", "Revoked"]

# Sidebar filters for drivers
with st.sidebar: 
    st.header("Filter Drivers")
    license_type = st.selectbox("License Type", LICENSE_TYPES)
    status = st.multiselect("License Status", STATUS_OPTIONS, default= ["Valid"])   
    age_range = st.slider("Age Range", 16, 100, (16, 100))
    sex_filter = st.radio ("Sex", ["All", "Male", "Female"], horizontal=True)
    st.button("Apply Filters", use_container_width=True)

# Fetch drivers based on filters
try: 
    drivers = dc.get_all_drivers(
        license_type=license_type,
        status=status,
        age_min=age_range[0],
        age_max=age_range[1],
        sex=sex_filter
    )
except Exception as e:
    st.error(f"Error fetching drivers: {e}")
    drivers = []

#Pagisipan q pa if lagyan metrics 

# Display driver data in a table
# Tabs for driver list, add driver, edit/delete driver 
# Will consider using buttons of add, edit, delete in the table itself for better UX 
tab1, tab2, tab3 = st.tabs(["Driver List", "Add Driver", "Edit/Delete Driver"])

with tab1: 
    if drivers:
        df = pd.DataFrame(drivers)
        rename_map = { 
            "full_name": "Full Name",
            "license_number": " Number",
            "license_type": " Type",
            "license_status": " Status",
            "birthday": "Birthday",
            "sex": "Sex",
            "address": "Address",
            "license_issuance_date": "Issuance",
            "license_expiration_date": "Expiration",
            "age": "Age",
        }
        df.rename(columns=rename_map, inplace=True)
        cols = ["Full Name", " Number", " Type", " Status", "Birthday",
                "Sex", "Address", "Issuance", "Expiration", "Age"]
        cols = [col for col in cols if col in df.columns]
        st.dataframe(df[cols], use_container_width=True)
        st.caption(f"Showing {total:,} records")
    else:
        st.info("No drivers found with the selected filters.")