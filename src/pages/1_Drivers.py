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

# Initialize values of filter options
if "filters" not in  st.session_state:
    st.session_state.filters = {
        "license_type": "All Types",
        "status": ["Valid"],
        "age_range": (16,100),
        "sex": "All"
    }

# Function to display filter dialog box 
@st.dialog("Filter Drivers")
def filter_dialog():
    st.write("Please fill in the following fields to filter the drivers:")
    
    # Filter options (can be changed)
    cur = st.session_state.filters 
    
    license_type = st.selectbox("License Type", LICENSE_TYPES, index=LICENSE_TYPES.index(cur["license_type"]))
    status = st.multiselect("License Status", STATUS_OPTIONS, default= cur["status"])
    age_range = st.slider("Age Range", 16, 100, cur["age_range"])
    sex_filter = st.radio ("Sex", ["All", "Male", "Female"], horizontal=True, index= ["All", "Male", "Female"].index(cur["sex"]))
    
    # Update filter options and rerun app when button is clicked
    # TEST LATER: width = 'stretch' or 'content'
    if st.button("Apply Filters", use_container_width=True, type="primary"):
        st.session_state.filters.update({
            "license_type": license_type,
            "status": status,
            "age_range": age_range,
            "sex": sex_filter,
        })
        st.rerun()

# ---------------------- CRUD OPERATIONS ---------------------- #
#form for adding a new driver 
@st.dialog("Add New Driver", width = "large")
def add_driver_dialog():
    # Form for adding a new driver
    with st.form("add_driver_form"):
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

        # Validate required fields 
        if st.form_submit_button("Add Driver", use_container_width=True, type="primary"):
            if not license_number or not full_name or not address:
                st.error("License number, full name, and address are required.")
            else:
                try:
                    # Add driver to the database
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

# Delete driver dialog
@st.dialog("Confirm Deletion")
def delete_driver_dialog(driver_data):
    st.warning(f"This will permanently delete **{d['full_name']}** and all linked records.")
    if st.button("Confirm Delete", type="primary"):
        try:
            dc.delete_driver(d["license_number"])
            st.success("Driver deleted.")
            st.rerun()
        except Exception as e:
            st.error(f"Error deleting record: {e}")

# Edit driver dialog
@st.dialog("Edit Driver Data", width = "large")
def edit_driver_dialog(d): #d = driver data
    cur_type = d.get("license_type")
    type_idx = TYPE_OPTIONS.index(cur_type) if cur_type in TYPE_OPTIONS else 0
    cur_stat = d.get("license_status", "Valid")
    stat_idx = STATUS_OPTIONS.index(cur_stat) if cur_stat in STATUS_OPTIONS else 0

    # Form for editing driver data
    with st.form("edit_driver_form"):
        c1, c2 = st.columns(2)
        
        with c1:
            new_name = st.text_input("Full Name", value=d.get("full_name", ""))
            new_bday = st.date_input("Date of Birth", value=d.get("birthday") or date.today())
            new_sex = st.selectbox("Sex", ["M", "F"], index=0 if d.get("sex") == "M" else 1)
            new_address = st.text_area("Address", value=d.get("address", ""))
                
        with c2:
            new_type = st.selectbox("License Type", TYPE_OPTIONS, index=type_idx)
            new_status = st.selectbox("Status", STATUS_OPTIONS, index=stat_idx)
            new_issue = st.date_input("Issuance Date", value=d.get("license_issuance_date") or date.today())
            new_exp = st.date_input("Expiration Date", value=d.get("license_expiration_date") or date.today())
            
        if st.form_submit_button("Save Changes", use_container_width=True):
            try:
                dc.update_driver(d["license_number"], {
                    "full_name": new_name,
                    "birthday": new_bday,
                    "sex": new_sex,
                    "address": new_address,
                    "license_type": new_type,
                    "license_status": new_status,
                    "license_issuance_date": new_issue,
                    "license_expiration_date": new_exp,
                })
                st.success("✅ Driver updated!")
                st.rerun()
            except Exception as e:
                st.error(f"Error updating record: {e}")

# ---------------------- END OF CRUD OPERATIONS ---------------------- #

col_search, empty_space, col_filter, col_add = st.columns([4, 1.5, 1.5, 2])
#empty_space essentially to move buttons to the right 

# Search bar 
with col_search:
    search_query = st.text_input("Search", placeholder="Search Driver Records", label_visibility = "collapsed")

# Filter button 
with col_filter: 
    if st.button("Filter", use_container_width = True):
        filter_dialog()

# Add Driver button 
with col_add:
    if st.button("Add Driver", use_container_width=True):
        add_driver_dialog()

f = st.session_state.filters
try: 
    drivers = dc.get_all_drivers( 
        license_type = f["license_type"],
        license_status = f["status"],
        age_range = f["age_range"],
        sex = f["sex"],
        search = search_query or None
    )
except Exception as e:
    st.error(f"Error loading drivers: {e}")
    drivers = []