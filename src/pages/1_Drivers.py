from datetime import date
import pandas as pd
import streamlit as st
from controllers import driver_controller as dc
from services import dashboard_service as dash_srv
from utils.ui_helpers import (
    css_style, render_sidebar, render_page_header,
    paginate_df, render_pagination_controls,
    apply_styler,
    color_license_status, format_license_status,
    color_license_type, format_license_type,
)

st.set_page_config(page_title="Driver Registry", layout="wide")
css_style(__file__)
render_sidebar()

@st.cache_data(ttl=60)
def _driver_metrics():
    return {
        "total":     dash_srv.get_total_drivers_count(),
        "valid":     dash_srv.get_valid_licenses_count(),
        "expired":   dash_srv.get_expired_licenses_count(),
        "suspended": dash_srv.get_suspended_licenses_count(),
    }

_dm = _driver_metrics()
render_page_header(
    title="👤 Driver Registry",
    subtitle="Manage and monitor driver information, licenses, violations, and other details.",
    metrics=[
        {"label": "👤 Total Drivers",    "value": f"{_dm['total']:,}"},
        {"label": "✅ Valid Licenses",     "value": f"{_dm['valid']:,}"},
        {"label": "🔴 Expired Licenses",   "value": f"{_dm['expired']:,}"},
        {"label": "⚠️ Suspended/Revoked", "value": f"{_dm['suspended']:,}"},
    ],
)
st.markdown("---")

# Filter option   #
LICENSE_TYPE_OPTIONS  = ["All Types", "Student", "Non-Professional", "Professional"]
LICENSE_STATUS_OPTIONS = ["All Statuses", "Valid", "Expired", "Suspended", "Revoked"]
TYPE_OPTS   = [t for t in LICENSE_TYPE_OPTIONS  if t != "All Types"]
STATUS_OPTS = [s for s in LICENSE_STATUS_OPTIONS if s != "All Statuses"]

#  defaults   #
if "filters" not in st.session_state:
    st.session_state.filters = {
        "license_type":   "All Types",    
        "license_status": "All Statuses", 
        "sex":            "All",         
        "min_age":        16,
        "max_age":        100,
    }
if "current_page" not in st.session_state:
    st.session_state.current_page = 1

# helper functions
def _sex_to_backend(label: str) -> str:
    return {"Male": "M", "Female": "F"}.get(label, "ALL")

def _type_to_backend(label: str) -> str:
    return "ALL" if label == "All Types" else label

def _status_to_backend(label: str) -> str:
    return "ALL" if label == "All Statuses" else label


#  DIALOGS  #

@st.dialog("Filter Drivers")
def filter_dialog():
    st.write("Fill in the fields below to filter the driver list.")
    cur = st.session_state.filters

    type_idx   = LICENSE_TYPE_OPTIONS.index(cur["license_type"]) if cur["license_type"] in LICENSE_TYPE_OPTIONS else 0
    status_idx = LICENSE_STATUS_OPTIONS.index(cur["license_status"]) if cur["license_status"] in LICENSE_STATUS_OPTIONS else 0
    sex_labels = ["All", "Male", "Female"]
    sex_map    = {"ALL": "All", "M": "Male", "F": "Female"}
    sex_idx    = sex_labels.index(sex_map.get(cur["sex"], "All"))

    license_type   = st.selectbox("License Type",   LICENSE_TYPE_OPTIONS,   index=type_idx)
    license_status = st.selectbox("License Status", LICENSE_STATUS_OPTIONS, index=status_idx)
    sex_label      = st.radio("Sex", sex_labels, index=sex_idx, horizontal=True)

    age_col1, age_col2 = st.columns(2)
    with age_col1:
        min_age = st.number_input("Min Age", min_value=0, max_value=150, value=cur["min_age"], step=1)
    with age_col2:
        max_age = st.number_input("Max Age", min_value=0, max_value=150, value=cur["max_age"], step=1)

    if st.button("Apply Filters", use_container_width=True, type="primary"):
        st.session_state.filters.update({
            "license_type":   license_type,
            "license_status": license_status,
            "sex":            _sex_to_backend(sex_label) if sex_label != "All" else "ALL",
            "min_age":        int(min_age),
            "max_age":        int(max_age),
        })
        st.session_state.current_page = 1
        st.rerun()

# add driver dialog
@st.dialog("Add New Driver", width="large")
def add_driver_dialog():
    with st.form("add_driver_form"):
        col1, col2 = st.columns(2)
        with col1:
            license_number = st.text_input("License Number *", placeholder="A01-15-100001")
            full_name      = st.text_input("Full Name *",      placeholder="Juan Dela Cruz")
            birthday       = st.date_input("Birthday *", min_value=date(1900, 1, 1), max_value=date.today())
            sex            = st.selectbox("Sex *", ["M", "F"])
            address        = st.text_input("Address *", placeholder="City, Province")
        with col2:
            license_type   = st.selectbox("License Type *",   TYPE_OPTS)
            license_status = st.selectbox("License Status *", STATUS_OPTS)
            issuance_date  = st.date_input("Issuance Date *",  value=date.today())
            expiration_date = st.date_input("Expiration Date *", value=date.today())
        if st.form_submit_button("Add Driver", use_container_width=True, type="primary"):
            if not license_number or not full_name or not address:
                st.error("License number, full name, and address are required.")
            else:
                try:
                    dc.create_driver({
                        "license_number":         license_number.strip().upper(),
                        "full_name":              full_name.strip(),
                        "birthday":               birthday,
                        "sex":                    sex,
                        "address":                address.strip(),
                        "license_type":           license_type,
                        "license_status":         license_status,
                        "license_issuance_date":  issuance_date,
                        "license_expiration_date": expiration_date,
                    })
                    st.success(f"✅ Driver '{full_name}' added successfully!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error adding driver: {e}")


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


@st.dialog("Edit Driver Data", width="large")
def edit_driver_dialog(d):
    cur_type = d.get("License Type", TYPE_OPTS[0])
    type_idx = TYPE_OPTS.index(cur_type) if cur_type in TYPE_OPTS else 0
    cur_stat = d.get("License Status", "Valid")
    stat_idx = STATUS_OPTS.index(cur_stat) if cur_stat in STATUS_OPTS else 0

    with st.form("edit_driver_form"):
        c1, c2 = st.columns(2)
        with c1:
            new_name    = st.text_input("Full Name",    value=d.get("Full Name", ""))
            new_bday    = st.date_input("Date of Birth", value=d.get("Birthday") or date.today())
            new_sex     = st.selectbox("Sex", ["M", "F"], index=0 if d.get("Sex") == "M" else 1)
            new_address = st.text_area("Address", value=d.get("Address", ""))
        with c2:
            new_type   = st.selectbox("License Type",   TYPE_OPTS,   index=type_idx)
            new_status = st.selectbox("License Status", STATUS_OPTS, index=stat_idx)
            new_issue  = st.date_input("Issuance Date",   value=d.get("Issuance Date")   or date.today())
            new_exp    = st.date_input("Expiration Date", value=d.get("Expiration Date") or date.today())
        if st.form_submit_button("Save Changes", use_container_width=True):
            try:
                dc.update_driver({
                    "license_number":          d["License Number"],
                    "full_name":               new_name,
                    "birthday":                new_bday,
                    "sex":                     new_sex,
                    "address":                 new_address,
                    "license_type":            new_type,
                    "license_status":          new_status,
                    "license_issuance_date":   new_issue,
                    "license_expiration_date": new_exp,
                })
                st.success("✅ Driver updated!")
                st.rerun()
            except Exception as e:
                st.error(f"Error updating record: {e}")

# ── Action bar ──
col_search, _, col_filter, col_add = st.columns([5, 0.3, 1.2, 1.5])
with col_search:
    search_query = st.text_input("Search", placeholder="Search Driver Records", label_visibility="collapsed")
with col_filter:
    if st.button("Filter", use_container_width=True):
        filter_dialog()
with col_add:
    if st.button("Add Driver", use_container_width=True):
        add_driver_dialog()


#  #
f = st.session_state.filters
try:
    drivers = dc.get_drivers_by_criteria({
        "license_type":   _type_to_backend(f["license_type"]),
        "license_status": _status_to_backend(f["license_status"]),
        "sex":            f["sex"],   # already "ALL" / "M" / "F"
        "min_age":        f["min_age"],
        "max_age":        f["max_age"],
    })
except Exception as e:
    st.error(f"Error loading drivers: {e}")
    drivers = []

action_bar = st.empty()

#  Build dataframe  #
if not drivers:
    st.info("No drivers found matching the current filters or search query.")
else:
    df = pd.DataFrame(drivers)

    # ── Calculate Age dynamically from birthday (never stored in DB) ──────── #
    if "birthday" in df.columns:
        df["birthday"] = pd.to_datetime(df["birthday"], errors="coerce").dt.date
        today = pd.Timestamp.today().normalize()
        df["age"] = df["birthday"].apply(
            lambda b: (
                today.year - b.year - ((today.month, today.day) < (b.month, b.day))
            ) if pd.notna(b) else None
        )

    rename_map = {
        "license_number":         "License Number",
        "full_name":              "Full Name",
        "birthday":               "Birthday",
        "age":                    "Age",
        "sex":                    "Sex",
        "address":                "Address",
        "license_type":           "License Type",
        "license_status":         "License Status",
        "license_issuance_date":  "Issuance Date",
        "license_expiration_date": "Expiration Date",
    }
    df.rename(columns=rename_map, inplace=True)

    display_cols = [
        "License Number", "Full Name", "Sex", "Birthday", "Age",
        "Address", "License Type", "License Status", "Issuance Date", "Expiration Date",
    ]
    df = df[[c for c in display_cols if c in df.columns]]

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
        paginated_df, start_idx, total_pages = paginate_df(df, "current_page", rows_per_page=10)

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