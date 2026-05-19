from datetime import date
import pandas as pd
import streamlit as st
from controllers import registration_controller as rc
from utils.ui_helpers import (
    css_style, paginate_df, render_pagination_controls,
    apply_styler, style_plate,
    color_reg_status, format_reg_status,
)

st.set_page_config(page_title="Vehicle Registrations", layout="wide")
css_style(__file__)

st.title("Vehicle Registrations")
st.markdown("Manage and track vehicle registration records, validity periods, and registration status.")
st.markdown("---")

STATUS_OPTIONS = ["Active", "Expired", "Suspended"]
VEHICLE_CATEGORIES = [
    "All Categories", "Sedan", "SUV", "Hatchback", "MPV", "Pickup",
    "Van", "Coupe", "Convertible", "Commercial Truck", "Bus", "Light Truck",
]

if "reg_filters" not in st.session_state:
    st.session_state.reg_filters = {
        "statuses":        ["Active"],
        "vehicle_category": "All Categories",
        "expired_as_of":   None,
    }
if "reg_page" not in st.session_state:
    st.session_state.reg_page = 1

@st.dialog("Filter Registrations")
def filter_dialog():
    st.write("Narrow results by registration status, vehicle category, or expiry date:")
    cur = st.session_state.reg_filters
    statuses = st.multiselect("Registration Status", STATUS_OPTIONS, default=cur["statuses"])
    cat_idx  = VEHICLE_CATEGORIES.index(cur["vehicle_category"]) if cur["vehicle_category"] in VEHICLE_CATEGORIES else 0
    vehicle_category = st.selectbox("Vehicle Category", VEHICLE_CATEGORIES, index=cat_idx)
    use_expiry = st.checkbox("Filter by expiration date (on or before)", value=cur["expired_as_of"] is not None)
    expired_as_of = None
    if use_expiry:
        expired_as_of = st.date_input("Expired As Of", value=cur["expired_as_of"] or date.today())
    if st.button("Apply Filters", use_container_width=True, type="primary"):
        st.session_state.reg_filters.update({
            "statuses":        statuses,
            "vehicle_category": vehicle_category,
            "expired_as_of":   expired_as_of,
        })
        st.session_state.reg_page = 1
        st.rerun()

@st.dialog("Add New Registration", width="large")
def add_registration_dialog():
    with st.form("add_registration_form"):
        col1, col2 = st.columns(2)
        with col1:
            reg_number   = st.text_input("Registration Number *", placeholder="CR-2025-XXXXXX")
            plate_number = st.text_input("Plate Number *",        placeholder="ABC1234")
            reg_date     = st.date_input("Registration Date *",   value=date.today())
        with col2:
            exp_date   = st.date_input("Expiration Date *", value=date.today())
            reg_status = st.selectbox("Registration Status *", STATUS_OPTIONS)
        if st.form_submit_button("Add Registration", use_container_width=True, type="primary"):
            if not reg_number or not plate_number:
                st.error("Registration number and plate number are required.")
            elif exp_date <= reg_date:
                st.error("Expiration date must be after the registration date.")
            else:
                try:
                    rc.add_registration({
                        "registration_number": reg_number.strip().upper(),
                        "plate_number":        plate_number.strip().upper(),
                        "registration_date":   reg_date,
                        "expiration_date":     exp_date,
                        "registration_status": reg_status,
                    })
                    st.success(f"✅ Registration '{reg_number.upper()}' added successfully!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error adding registration: {e}")

@st.dialog("Confirm Deletion")
def delete_registration_dialog(r):
    st.warning(
        f"This will permanently delete registration **{r['Registration No.']}** "
        f"for plate **{r['Plate Number']}**."
    )
    if st.button("Confirm Delete", type="primary", use_container_width=True):
        try:
            rc.delete_registration(r["Registration No."])
            st.success("Registration deleted.")
            st.rerun()
        except Exception as e:
            st.error(f"Error deleting record: {e}")

@st.dialog("Edit Registration", width="large")
def edit_registration_dialog(r):
    stat_idx = STATUS_OPTIONS.index(r["Status"]) if r["Status"] in STATUS_OPTIONS else 0
    with st.form("edit_registration_form"):
        col1, col2 = st.columns(2)
        with col1:
            st.text_input("Registration No. (read-only)", value=r["Registration No."], disabled=True)
            new_plate    = st.text_input("Plate Number", value=r["Plate Number"])
            new_reg_date = st.date_input(
                "Registration Date",
                value=r["Registration Date"] if isinstance(r["Registration Date"], date) else date.today()
            )
        with col2:
            new_exp_date = st.date_input(
                "Expiration Date",
                value=r["Expiration Date"] if isinstance(r["Expiration Date"], date) else date.today()
            )
            new_status = st.selectbox("Status", STATUS_OPTIONS, index=stat_idx)
        if st.form_submit_button("Save Changes", use_container_width=True):
            if new_exp_date <= new_reg_date:
                st.error("Expiration date must be after the registration date.")
            else:
                try:
                    rc.update_registration(r["Registration No."], {
                        "registration_date":   new_reg_date,
                        "expiration_date":     new_exp_date,
                        "registration_status": new_status,
                        "plate_number":        new_plate.strip().upper(),
                    })
                    st.success("✅ Registration updated!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error updating record: {e}")

col_search, empty_space, col_filter, col_add = st.columns([4, 1.5, 1.5, 2])

with col_search:
    search_query = st.text_input("Search", placeholder="Search by registration number, plate, or owner...", label_visibility="collapsed")

with col_filter:
    if st.button("Filter", use_container_width=True):
        filter_dialog()

with col_add:
    if st.button("Add Registration", use_container_width=True):
        add_registration_dialog()

f = st.session_state.reg_filters
try:
    registrations = rc.get_all_registrations(
        statuses=f["statuses"] if f["statuses"] else None,
        vehicle_category=f["vehicle_category"],
        expired_as_of=f["expired_as_of"],
    )
except Exception as e:
    st.error(f"Error loading registrations: {e}")
    registrations = []

action_bar = st.empty()

if not registrations:
    st.info("No registrations found matching the current filters or search query.")
else:
    df = pd.DataFrame(registrations)

    rename_map = {
        "registration_number":"Registration No.",
        "plate_number":"Plate Number",
        "registration_date":"Registration Date",
        "expiration_date":"Expiration Date",
        "registration_status":"Status",
        "make":"Make",
        "model":"Model",
        "vehicle_type":"Vehicle Type",
        "owner_name":"Owner",
    }
    df.rename(columns=rename_map, inplace=True)
    display_cols = [
        "Registration No.", "Owner", "Plate Number",
        "Make", "Model", "Registration Date", "Expiration Date", "Status",
    ]
    df = df[[c for c in display_cols if c in df.columns]]

    if search_query:
        sq = search_query.lower()
        mask = (
            df["Registration No."].str.lower().str.contains(sq, na=False) |
            df["Plate Number"].str.lower().str.contains(sq, na=False) |
            df["Owner"].str.lower().str.contains(sq, na=False)
        )
        df = df[mask]

    if df.empty:
        st.info("No registrations found matching the current filters or search query.")
    else:
        paginated_df, start_idx, total_pages = paginate_df(df, "reg_page", rows_per_page=10)

        styler = paginated_df.style.format({"Status": format_reg_status})
        styler = apply_styler(styler, color_reg_status, subset=["Status"])
        styler = apply_styler(styler, style_plate,      subset=["Plate Number"])
        styled_df = styler.set_properties(**{"text-align": "center"})

        selection_event = st.dataframe(
            styled_df,
            use_container_width=True,
            hide_index=True,
            on_select="rerun",
            selection_mode="single-row",
        )

        render_pagination_controls("reg_page", total_pages, paginated_df)

        selected_rows = selection_event.selection.rows
        if selected_rows:
            selected_data = paginated_df.iloc[selected_rows[0]].to_dict()

            with action_bar.container():
                with st.container(border=True):
                    c_text, c_edit, c_del = st.columns([6, 1.5, 1.5])
                    with c_text:
                        st.markdown(
                            f"**Active Record:** {selected_data['Registration No.']} "
                            f"(`{selected_data['Plate Number']}`)"
                        )
                    with c_edit:
                        if st.button("Edit", use_container_width=True, key="edit_reg"):
                            edit_registration_dialog(selected_data)
                    with c_del:
                        if st.button("Delete", type="primary", use_container_width=True, key="del_reg"):
                            delete_registration_dialog(selected_data)