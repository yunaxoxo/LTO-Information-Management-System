from datetime import date
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
        # Convert to DataFrame 
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
        # Rename columns for better display
        df.rename(columns=rename_map, inplace=True)
        cols = ["Full Name", " Number", " Type", " Status", "Birthday",
                "Sex", "Address", "Issuance", "Expiration", "Age"]
        cols = [col for col in cols if col in df.columns]
        st.dataframe(df[cols], use_container_width=True)
    else:
        st.info("No drivers found with the selected filters.")

# Add new driver
with tab2: 
    st.markdown("Add New Driver")
    st.caption("License format: XXX-XX-XXXXXX")
    with st.form("add_driver_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            license_number = st.text_input("License Number*", placeholder="XXX-XX-XXXXXX")
            full_name = st.text_input("Full Name*", placeholder="Juan Dela Cruz")
            birthday = st.date_input("Birthday*", min_value=date(1900, 1, 1), max_value=date.today())
            sex = st.selectbox("Sex", ["M", "F"])
            address = st.text_input("Address*", placeholder="City, Province")
        with col2:
            license_type_in = st.selectbox("License Type *", TYPE_OPTIONS)
            license_status = st.selectbox("License Status *", STATUS_OPTIONS)
            issuance_date = st.date_input("Issuance Date *", value=date.today())
            expiration_date = st.date_input("Expiration Date *", value=date.today())
        submitted = st.form_submit_button("Add Driver", use_container_width=True)
        if submitted:
            if not all([license_number, full_name, address]):
                st.error("License number, full name, and address are required.")
            else:
                try:
                    dc.add_driver({
                        "license_number": license_number.strip().upper(),
                        "full_name": full_name.strip(),
                        "birthday": birthday,
                        "sex": sex,
                        "address": address.strip(),
                        "license_type": license_type_in,
                        "license_status": license_status,
                        "license_issuance_date": issuance_date,
                        "license_expiration_date": expiration_date,
                    })
                    st.success(f"✅ Driver '{full_name}' added successfully!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error adding driver: {e}")
