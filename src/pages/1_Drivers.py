from datetime import date
import pandas as pd
import streamlit as st
from controllers import driver_controller as dc
from utils.ui_helpers import (
    css_style, safe_str, paginate_df, render_pagination_controls,
    apply_styler,
    color_license_status, format_license_status,
    color_license_type, format_license_type,
)

st.set_page_config(page_title="Driver Registry", layout="wide")
css_style(__file__)

st.title("Driver Registry")
st.markdown("Manage and monitor driver information, including licenses, violations, and other details.")
st.markdown("---")

# Define filter options #
LICENSE_TYPES = ["All Types", "Student", "Non-Professional", "Professional"]
TYPE_OPTIONS  = [t for t in LICENSE_TYPES if t != "All Types"]
STATUS_OPTIONS = ["Valid", "Expired", "Suspended", "Revoked"]

# Initialize values of session state #
if "filters" not in st.session_state:
    st.session_state.filters = {
        "license_type": "All Types",
        "status": ["Valid"],
        "age_range": (16, 100),
        "sex": "All",
    }

if "current_page" not in st.session_state:
    st.session_state.current_page = 1

# ---------------------- DIALOGS ---------------------- #
# Filter dialog for drivers 
@st.dialog("Filter Drivers")
def filter_dialog():
    st.write("Please fill in the following fields to filter the drivers:")
    cur = st.session_state.filters
    license_type = st.selectbox("License Type", LICENSE_TYPES, index=LICENSE_TYPES.index(cur["license_type"]))
    status       = st.multiselect("License Status", STATUS_OPTIONS, default=cur["status"])
    age_range    = st.slider("Age Range", 16, 100, cur["age_range"])
    sex_filter   = st.radio("Sex", ["All", "Male", "Female"], horizontal=True,
                            index=["All", "Male", "Female"].index(cur["sex"]))
    if st.button("Apply Filters", use_container_width=True, type="primary"):
        st.session_state.filters.update({
            "license_type": license_type,
            "status": status,
            "age_range": age_range,
            "sex": sex_filter,
        })
        st.session_state.current_page = 1
        st.rerun() # refreshes the page to apply filters

# form for adding a new driver 
@st.dialog("Add New Driver", width="large")
def add_driver_dialog():
    with st.form("add_driver_form"):
        col1, col2 = st.columns(2)
        with col1:
            license_number = st.text_input("License Number*", placeholder="XXX-XX-XXXXXX")
            full_name      = st.text_input("Full Name*", placeholder="Juan Dela Cruz")
            birthday       = st.date_input("Birthday*", min_value=date(1900, 1, 1), max_value=date.today())
            sex            = st.selectbox("Sex", ["M", "F"])
            address        = st.text_input("Address*", placeholder="City, Province")
        with col2:
            license_type_in = st.selectbox("License Type *", TYPE_OPTIONS)
            license_status  = st.selectbox("License Status *", STATUS_OPTIONS)
            issuance_date   = st.date_input("Issuance Date *", value=date.today())
            expiration_date = st.date_input("Expiration Date *", value=date.today())
        if st.form_submit_button("Add Driver", use_container_width=True, type="primary"):
            if not license_number or not full_name or not address:
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

# dialog for deleting a driver #
@st.dialog("Confirm Deletion")
def delete_driver_dialog(d):
    st.warning(f"This will permanently delete **{d['Full Name']}** and all linked records.")
    if st.button("Confirm Delete", type="primary", use_container_width=True):
        try:
            dc.delete_driver(d["License Number"])
            st.success("Driver deleted.")
            st.rerun()
        except Exception as e:
            st.error(f"Error deleting record: {e}")

# dialog for editing a driver #
@st.dialog("Edit Driver Data", width="large")
def edit_driver_dialog(d):
    cur_type = d.get("License Type")
    type_idx = TYPE_OPTIONS.index(cur_type) if cur_type in TYPE_OPTIONS else 0
    cur_stat = d.get("License Status", "Valid")
    stat_idx = STATUS_OPTIONS.index(cur_stat) if cur_stat in STATUS_OPTIONS else 0
    with st.form("edit_driver_form"):
        c1, c2 = st.columns(2)
        with c1:
            new_name    = st.text_input("Full Name", value=d.get("Full Name", ""))
            new_bday    = st.date_input("Date of Birth", value=d.get("Birthday") or date.today())
            new_sex     = st.selectbox("Sex", ["M", "F"], index=0 if d.get("Sex") == "M" else 1)
            new_address = st.text_area("Address", value=d.get("Address", ""))
        with c2:
            new_type   = st.selectbox("License Type", TYPE_OPTIONS, index=type_idx)
            new_status = st.selectbox("Status", STATUS_OPTIONS, index=stat_idx)
            new_issue  = st.date_input("Issuance Date", value=d.get("Issuance Date") or date.today())
            new_exp    = st.date_input("Expiration Date", value=d.get("Expiration Date") or date.today())
        if st.form_submit_button("Save Changes", use_container_width=True):
            try:
                dc.update_driver(d["License Number"], {
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

# top nav bar #
col_search, empty_space, col_filter, col_add = st.columns([4, 1.5, 1.5, 2])
with col_search:
    search_query = st.text_input("Search", placeholder="Search Driver Records", label_visibility="collapsed")
with col_filter:
    if st.button("Filter", use_container_width=True):
        filter_dialog()
with col_add:
    if st.button("Add Driver", use_container_width=True):
        add_driver_dialog()

# get data #
f = st.session_state.filters
try:
    drivers = dc.get_all_drivers(
        license_type=f["license_type"],
        statuses=f["status"],
        age_min=f["age_range"][0],
        age_max=f["age_range"][1],
        sex=f["sex"],
    )
except Exception as e:
    st.error(f"Error loading drivers: {e}")
    drivers = []

# placeholder to be used later 
action_bar = st.empty()

# dataframe  #
if not drivers:
    st.info("No drivers found matching the current filters or search query.")
else:
    #rename columns 
    df = pd.DataFrame(drivers)
    rename_map = {
        "license_number":"License Number",
        "full_name":"Full Name",
        "birthday":"Birthday",
        "age":"Age",
        "sex":"Sex",
        "address":"Address",
        "license_type":"License Type",
        "license_status":"License Status",
        "license_issuance_date":"Issuance Date",
        "license_expiration_date":"Expiration Date",
    }
    df.rename(columns=rename_map, inplace=True)

    # column names 
    cols = ["License Number", "Full Name", "Sex", "Birthday", "Age",
            "Address", "License Type", "License Status", "Issuance Date", "Expiration Date"]
    df = df[[c for c in cols if c in df.columns]]

    if search_query:
        sq = search_query.lower()
        mask = (
            df["Full Name"].str.lower().str.contains(sq, na=False) |
            df["License Number"].str.lower().str.contains(sq, na=False)
        )
        df = df[mask]

    if df.empty:
        st.info("No drivers found matching the current filters or search query.")
    else:
        #  Pagination
        paginated_df, start_idx, total_pages = paginate_df(df, "current_page", rows_per_page=10)

        #  Styling 
        styler = paginated_df.style.format({
            "License Status": format_license_status,
            "License Type":   format_license_type,
        })
        styler = apply_styler(styler, color_license_status, subset=["License Status"])
        styler = apply_styler(styler, color_license_type,   subset=["License Type"])
        styled_df = styler.set_properties(**{"text-align": "center"})

        selection_event = st.dataframe(
            styled_df, use_container_width=True, hide_index=True,
            on_select="rerun", selection_mode="single-row",
        )

        render_pagination_controls("current_page", total_pages, paginated_df)

        # Contextual Action Bar 
        selected_rows = selection_event.selection.rows
        if selected_rows:
            selected_driver_data = paginated_df.iloc[selected_rows[0]].to_dict()
            with action_bar.container():
                with st.container(border=True):
                    c_text, c_edit, c_del = st.columns([6, 1.5, 1.5])
                    with c_text:
                        st.markdown(
                            f"**Active Record:** {selected_driver_data['Full Name']} "
                            f"(`{selected_driver_data['License Number']}`)"
                        )
                    with c_edit:
                        if st.button("Edit", use_container_width=True, key="edit_driver"):
                            edit_driver_dialog(selected_driver_data)
                    with c_del:
                        if st.button("Delete", type="primary", use_container_width=True, key="del_driver"):
                            delete_driver_dialog(selected_driver_data)