from datetime import date
import pandas as pd
import streamlit as st
from controllers import violation_controller as vioc
from utils.ui_helpers import (
    css_style, safe_str, paginate_df, render_pagination_controls,
    apply_styler,
    color_violation_status, format_violation_status, format_fine,
)

st.set_page_config(page_title="Traffic Violations", layout="wide")
css_style(__file__)

st.title("Traffic Violations")
st.markdown("Track and manage all recorded traffic infractions, fines, and enforcement actions.")
st.markdown("---")

STATUS_OPTIONS = ["Unpaid", "Paid", "Contested"]
VIOLATION_TYPES = [
    "Speeding", "Reckless Driving", "Illegal Parking", "Obstruction",
    "Illegal Turn", "Lane Straddling", "No Seatbelt", "No Helmet",
    "Coding Violation", "Smoke Belching", "Overloading", "Invalid Registration",
    "Disregarding Traffic Sign", "Driving with Expired License",
    "Jaywalking near Footbridge", "Disobeying Traffic Officer", "Other",
]

if "vio_filters" not in st.session_state:
    st.session_state.vio_filters = {
        "statuses":    [],
        "date_start":  None,
        "date_end":    None,
        "driver_name": "",
    }
if "vio_page" not in st.session_state:
    st.session_state.vio_page = 1

@st.dialog("Filter Violations")
def filter_dialog():
    st.write("Narrow results by status, date range, or driver name:")
    cur = st.session_state.vio_filters
    statuses    = st.multiselect("Payment Status", STATUS_OPTIONS, default=cur["statuses"])
    driver_name = st.text_input("Driver Name (contains)", value=cur["driver_name"])
    use_date_range = st.checkbox(
        "Filter by date range",
        value=(cur["date_start"] is not None or cur["date_end"] is not None)
    )
    date_start = date_end = None
    if use_date_range:
        dc1, dc2 = st.columns(2)
        with dc1:
            date_start = st.date_input("From", value=cur["date_start"] or date(2025, 1, 1))
        with dc2:
            date_end = st.date_input("To", value=cur["date_end"] or date.today())
    if st.button("Apply Filters", use_container_width=True, type="primary"):
        st.session_state.vio_filters.update({
            "statuses":    statuses,
            "date_start":  date_start,
            "date_end":    date_end,
            "driver_name": driver_name.strip(),
        })
        st.session_state.vio_page = 1
        st.rerun()

@st.dialog("Add New Violation", width="large")
def add_violation_dialog():
    try:
        suggested_top = vioc.generate_top_number()
    except Exception:
        suggested_top = ""

    with st.form("add_violation_form"):
        col1, col2 = st.columns(2)
        with col1:
            top_number     = st.text_input("TOP Number *", value=suggested_top, placeholder="T-YYMMDD-NNNNNNN")
            violation_type = st.selectbox("Violation Type *", VIOLATION_TYPES)
            violation_date = st.date_input("Violation Date *", value=date.today())
            violation_time = st.time_input("Violation Time *")
            location       = st.text_input("Location *", placeholder="EDSA Kamuning, Quezon City")
        with col2:
            apprehending_officer = st.text_input("Apprehending Officer *", placeholder="Officer J. Santos")
            violation_status     = st.selectbox("Status *", STATUS_OPTIONS)
            fine_amount          = st.number_input("Fine Amount (₱) *", min_value=0, step=100, value=1000)
            license_number       = st.text_input("Driver License Number *", placeholder="A01-15-100001")
            plate_number         = st.text_input("Plate Number (optional)", placeholder="ABC1234")
        if st.form_submit_button("Add Violation", use_container_width=True, type="primary"):
            if not all([top_number, location, apprehending_officer, license_number]):
                st.error("TOP number, location, officer, and license number are required.")
            else:
                try:
                    from datetime import datetime
                    vioc.add_violation({
                        "top_number": top_number.strip().upper(),
                        "violation_type": violation_type,
                        "violation_date": datetime.combine(violation_date, violation_time),
                        "location": location.strip(),
                        "apprehending_officer": apprehending_officer.strip(),
                        "violation_status": violation_status,
                        "fine_amount": int(fine_amount),
                        "license_number": license_number.strip().upper(),
                        "plate_number": plate_number.strip().upper() if plate_number.strip() else None,
                    })
                    st.success(f"✅ Violation '{top_number.upper()}' recorded successfully!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error adding violation: {e}")

@st.dialog("Confirm Deletion")
def delete_violation_dialog(v):
    st.warning(
        f"This will permanently delete violation **{v['TOP Number']}** "
        f"({v.get('Violation Type', '')}) for license **{v.get('License No.', '')}**."
    )
    if st.button("Confirm Delete", type="primary", use_container_width=True):
        try:
            vioc.delete_violation(v["violation_id"])
            st.success("Violation record deleted.")
            st.rerun()
        except Exception as e:
            st.error(f"Error deleting record: {e}")

@st.dialog("Edit Violation", width="large")
def edit_violation_dialog(v):
    stat_idx  = STATUS_OPTIONS.index(v["Status"]) if v.get("Status") in STATUS_OPTIONS else 0
    vtype_idx = VIOLATION_TYPES.index(v["Violation Type"]) if v.get("Violation Type") in VIOLATION_TYPES else 0

    raw_date = v.get("Date & Time")
    if hasattr(raw_date, "date"):
        cur_date, cur_time = raw_date.date(), raw_date.time()
    elif isinstance(raw_date, date):
        cur_date, cur_time = raw_date, None
    else:
        cur_date, cur_time = date.today(), None

    with st.form("edit_violation_form"):
        col1, col2 = st.columns(2)
        with col1:
            st.text_input("TOP Number (read-only)", value=v.get("TOP Number", ""), disabled=True)
            new_type     = st.selectbox("Violation Type", VIOLATION_TYPES, index=vtype_idx)
            new_date     = st.date_input("Violation Date", value=cur_date)
            new_time     = st.time_input("Violation Time",  value=cur_time)
            new_location = st.text_input("Location", value=v.get("Location", ""))
        with col2:
            new_officer = st.text_input("Apprehending Officer", value=v.get("Officer", ""))
            new_status  = st.selectbox("Status", STATUS_OPTIONS, index=stat_idx)
            new_fine    = st.number_input("Fine Amount (₱)", min_value=0, step=100, value=int(v.get("Fine (₱)", 0)))
            new_license = st.text_input("Driver License Number", value=v.get("License No.", ""))
            new_plate   = st.text_input("Plate Number (optional)", value=v.get("Plate No.", "") or "")
        if st.form_submit_button("Save Changes", use_container_width=True):
            try:
                from datetime import datetime
                vioc.update_violation(v["violation_id"], {
                    "violation_type":new_type,
                    "violation_date":datetime.combine(new_date, new_time),
                    "location":new_location,
                    "apprehending_officer":new_officer,
                    "violation_status":new_status,
                    "fine_amount":int(new_fine),
                    "license_number":new_license.strip().upper(),
                    "plate_number":new_plate.strip().upper() if new_plate.strip() else None,
                })
                st.success("✅ Violation updated!")
                st.rerun()
            except Exception as e:
                st.error(f"Error updating record: {e}")

col_search, empty_space, col_filter, col_add = st.columns([4, 1.5, 1.5, 2])

with col_search:
    search_query = st.text_input(
        "Search", placeholder="Search by TOP number, type, location, license, or plate...",
        label_visibility="collapsed"
    )

with col_filter:
    if st.button("Filter", use_container_width=True):
        filter_dialog()

with col_add:
    if st.button("Add Violation", use_container_width=True):
        add_violation_dialog()

f = st.session_state.vio_filters
try:
    violations = vioc.get_all_violations(
        driver_name=f["driver_name"] or None,
        date_start=f["date_start"],
        date_end=f["date_end"],
    )
except Exception as e:
    st.error(f"Error loading violations: {e}")
    violations = []

if not violations:
    st.info("No violations found matching the current filters or search query.")
else:
    df = pd.DataFrame(violations)

    rename_map = {
        "violation_id":         "violation_id",
        "top_number":           "TOP Number",
        "violation_type":       "Violation Type",
        "violation_date":       "Date & Time",
        "location":             "Location",
        "apprehending_officer": "Officer",
        "violation_status":     "Status",
        "fine_amount":          "Fine (₱)",
        "license_number":       "License No.",
        "plate_number":         "Plate No.",
        "driver_name":          "Driver",
    }
    df.rename(columns=rename_map, inplace=True)

    df["VEHICLE / PLATE"] = safe_str(df["Plate No."].fillna("—"))

    if search_query:
        sq = search_query.lower()
        mask = (
            df["TOP Number"].str.lower().str.contains(sq, na=False) |
            df["Violation Type"].str.lower().str.contains(sq, na=False) |
            df["Location"].str.lower().str.contains(sq, na=False) |
            df["License No."].str.lower().str.contains(sq, na=False) |
            df["Plate No."].fillna("").str.lower().str.contains(sq, na=False) |
            df["Driver"].str.lower().str.contains(sq, na=False)
        )
        df = df[mask]

    if df.empty:
        st.info("No violations found matching the current filters or search query.")
    else:
        display_cols = [
            "Violation Type", "TOP Number", "Date & Time", "Location",
            "Driver", "License No.", "VEHICLE / PLATE",
            "Fine (₱)", "Status", "Officer",
        ]

        full_cols  = display_cols + ["violation_id", "Plate No."]
        df_full    = df[[c for c in full_cols     if c in df.columns]].copy()
        df_display = df[[c for c in display_cols  if c in df.columns]].copy()

        paginated_display, start_idx, total_pages = paginate_df(df_display, "vio_page", rows_per_page=10)

        styler = paginated_display.style.format({
            "Status":   format_violation_status,
            "Fine (₱)": format_fine,
        })
        styler = apply_styler(styler, color_violation_status, subset=["Status"])
        styled_df = styler.set_properties(**{"text-align": "center", "white-space": "pre-wrap"})

        selection_event = st.dataframe(
            styled_df,
            use_container_width=True,
            hide_index=True,
            on_select="rerun",
            selection_mode="single-row",
        )

        render_pagination_controls("vio_page", total_pages, paginated_display)

        selected_rows = selection_event.selection.rows
        if selected_rows:
            
            full_row = df_full.iloc[start_idx + selected_rows[0]].to_dict()

            with action_bar.container():
                with st.container(border=True):
                    c_text, c_edit, c_del = st.columns([6, 1.5, 1.5])
                    with c_text:
                        st.markdown(
                            f"**Active Record:** {full_row.get('Violation Type', '')} — "
                            f"`{full_row.get('TOP Number', '')}`"
                        )
                    with c_edit:
                        if st.button("Edit", use_container_width=True, key="edit_vio"):
                            edit_violation_dialog(full_row)
                    with c_del:
                        if st.button("Delete", type="primary", use_container_width=True, key="del_vio"):
                            delete_violation_dialog(full_row)