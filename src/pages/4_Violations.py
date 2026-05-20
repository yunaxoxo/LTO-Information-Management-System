from datetime import date, datetime

import pandas as pd
import streamlit as st

from controllers import violation_controller as vioc
from utils.ui_helpers import (
    apply_styler,
    color_violation_status,
    css_style,
    format_fine,
    format_violation_status,
    paginate_df,
    render_pagination_controls,
)

st.set_page_config(page_title="Traffic Violations", layout="wide")
css_style(__file__)

st.title("Traffic Violations")
st.markdown(
    "Track and manage all recorded traffic infractions, fines, and enforcement actions."
)
st.markdown("---")

STATUS_FILTER_OPTIONS = ["All Statuses", "Unpaid", "Paid", "Contested"]
STATUS_OPTS = [s for s in STATUS_FILTER_OPTIONS if s != "All Statuses"]

VIOLATION_TYPE_FILTER_OPTIONS = [
    "All Types",
    "Speeding",
    "Reckless Driving",
    "Illegal Parking",
    "Obstruction",
    "Illegal Turn",
    "Lane Straddling",
    "No Seatbelt",
    "No Helmet",
    "Coding Violation",
    "Smoke Belching",
    "Overloading",
    "Invalid Registration",
    "Disregarding Traffic Sign",
    "Driving with Expired License",
    "Jaywalking near Footbridge",
    "Disobeying Traffic Officer",
    "Other",
]
VIOLATION_TYPES = [t for t in VIOLATION_TYPE_FILTER_OPTIONS if t != "All Types"]

if "vio_filters" not in st.session_state:
    st.session_state.vio_filters = {
        "violation_status": "All Statuses",
        "violation_type": "All Types",
        "location_like": "",
        "date_mode": "Any Date",
        "date_year": date.today().year,
        "date_from": None,
        "date_to": None,
    }
if "vio_page" not in st.session_state:
    st.session_state.vio_page = 1


def _status_to_backend(label: str) -> str:
    return "ALL" if label == "All Statuses" else label


def _vtype_to_backend(label: str) -> str:
    return "ALL" if label == "All Types" else label


DATE_MODE_OPTIONS = ["Any Date", "Single Year", "Date Range"]


@st.dialog("Filter Violations", width="large")
def filter_dialog():
    st.write("Narrow results by status, type, location, or date:")
    cur = st.session_state.vio_filters

    col1, col2 = st.columns(2)
    with col1:
        stat_idx = (
            STATUS_FILTER_OPTIONS.index(cur["violation_status"])
            if cur["violation_status"] in STATUS_FILTER_OPTIONS
            else 0
        )
        violation_status = st.selectbox(
            "Payment Status", STATUS_FILTER_OPTIONS, index=stat_idx
        )
    with col2:
        vtype_idx = (
            VIOLATION_TYPE_FILTER_OPTIONS.index(cur["violation_type"])
            if cur["violation_type"] in VIOLATION_TYPE_FILTER_OPTIONS
            else 0
        )
        violation_type = st.selectbox(
            "Violation Type", VIOLATION_TYPE_FILTER_OPTIONS, index=vtype_idx
        )

    st.markdown("**Location**")
    location_like = st.text_input(
        "City or Region (partial match)",
        value=cur.get("location_like", ""),
        placeholder="e.g. Quezon City, EDSA, Makati",
        help="Filters violations whose location contains this text (case-insensitive).",
    )

    st.markdown("**Date Filter**")
    cur_mode = cur.get("date_mode", "Any Date")
    mode_idx = DATE_MODE_OPTIONS.index(cur_mode) if cur_mode in DATE_MODE_OPTIONS else 0
    date_mode = st.radio(
        "Date selection mode",
        DATE_MODE_OPTIONS,
        index=mode_idx,
        horizontal=True,
        label_visibility="collapsed",
    )

    new_date_year = cur.get("date_year") or date.today().year
    new_date_from = cur.get("date_from")
    new_date_to = cur.get("date_to")

    if date_mode == "Single Year":
        current_yr = date.today().year
        year_options = list(range(current_yr, current_yr - 15, -1))
        yr_idx = (
            year_options.index(new_date_year) if new_date_year in year_options else 0
        )
        new_date_year = st.selectbox(
            "Select Year", options=year_options, index=yr_idx, key="fd_year"
        )
        new_date_from = new_date_to = None
    elif date_mode == "Date Range":
        dcol1, dcol2 = st.columns(2)
        with dcol1:
            new_date_from = st.date_input(
                "From",
                value=new_date_from or date.today().replace(day=1),
                key="fd_from",
            )
        with dcol2:
            new_date_to = st.date_input(
                "To",
                value=new_date_to or date.today(),
                key="fd_to",
            )
        new_date_year = None
        if new_date_from and new_date_to and new_date_from > new_date_to:
            st.error("'From' date must be before 'To' date.")
            return
    else:
        new_date_year = new_date_from = new_date_to = None

    if date_mode == "Single Year" and new_date_year:
        resolved_from = date(new_date_year, 1, 1)
        resolved_to = date(new_date_year, 12, 31)
    elif date_mode == "Date Range":
        resolved_from, resolved_to = new_date_from, new_date_to
    else:
        resolved_from = resolved_to = None

    st.markdown("")
    bcol1, bcol2 = st.columns(2)
    with bcol1:
        if st.button("Clear Filters", use_container_width=True):
            st.session_state.vio_filters = {
                "violation_status": "All Statuses",
                "violation_type": "All Types",
                "location_like": "",
                "date_mode": "Any Date",
                "date_year": date.today().year,
                "date_from": None,
                "date_to": None,
            }
            st.session_state.vio_page = 1
            st.rerun()
    with bcol2:
        if st.button("Apply Filters", use_container_width=True, type="primary"):
            st.session_state.vio_filters.update(
                {
                    "violation_status": violation_status,
                    "violation_type": violation_type,
                    "location_like": location_like.strip(),
                    "date_mode": date_mode,
                    "date_year": new_date_year,
                    "date_from": resolved_from,
                    "date_to": resolved_to,
                }
            )
            st.session_state.vio_page = 1
            st.rerun()


@st.dialog("Add New Violation", width="large")
def add_violation_dialog():
    with st.form("add_violation_form"):
        col1, col2 = st.columns(2)
        with col1:
            top_number = st.text_input("TOP Number *", placeholder="T-YYMMDD-NNNNNNN")
            violation_type = st.selectbox("Violation Type *", VIOLATION_TYPES)
            violation_date = st.date_input("Violation Date *", value=date.today())
            violation_time = st.time_input("Violation Time *")
            location = st.text_input(
                "Location *", placeholder="EDSA Kamuning, Quezon City"
            )
        with col2:
            apprehending_officer = st.text_input(
                "Apprehending Officer *", placeholder="Officer J. Santos"
            )
            violation_status = st.selectbox("Status *", STATUS_OPTS)
            fine_amount = st.number_input(
                "Fine Amount (₱) *", min_value=0, step=100, value=1000
            )
            license_number = st.text_input(
                "Driver License Number *", placeholder="A01-15-100001"
            )
            plate_number = st.text_input(
                "Plate Number (optional)", placeholder="ABC1234"
            )
        if st.form_submit_button(
            "Add Violation", use_container_width=True, type="primary"
        ):
            if not all([top_number, location, apprehending_officer, license_number]):
                st.error(
                    "TOP number, location, officer, and license number are required."
                )
            else:
                try:
                    vioc.create_violation(
                        {
                            "top_number": top_number.strip().upper(),
                            "violation_type": violation_type,
                            "violation_date": datetime.combine(
                                violation_date, violation_time
                            ),
                            "location": location.strip(),
                            "apprehending_officer": apprehending_officer.strip(),
                            "violation_status": violation_status,
                            "fine_amount": int(fine_amount),
                            "license_number": license_number.strip().upper(),
                            "plate_number": plate_number.strip().upper()
                            if plate_number.strip()
                            else None,
                        }
                    )
                    st.success(
                        f"✅ Violation '{top_number.upper()}' recorded successfully!"
                    )
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
            vioc.delete_violation(v["TOP Number"])
            st.success("Violation record deleted.")
            st.rerun()
        except Exception as e:
            st.error(f"Error deleting record: {e}")


@st.dialog("Edit Violation", width="large")
def edit_violation_dialog(v):
    stat_idx = STATUS_OPTS.index(v["Status"]) if v.get("Status") in STATUS_OPTS else 0
    vtype_idx = (
        VIOLATION_TYPES.index(v["Violation Type"])
        if v.get("Violation Type") in VIOLATION_TYPES
        else 0
    )
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
            st.text_input(
                "TOP Number (read-only)", value=v.get("TOP Number", ""), disabled=True
            )
            new_type = st.selectbox("Violation Type", VIOLATION_TYPES, index=vtype_idx)
            new_date = st.date_input("Violation Date", value=cur_date)
            new_time = st.time_input("Violation Time", value=cur_time)
            new_location = st.text_input("Location", value=v.get("Location", ""))
        with col2:
            new_officer = st.text_input(
                "Apprehending Officer", value=v.get("Officer", "")
            )
            new_status = st.selectbox("Status", STATUS_OPTS, index=stat_idx)
            new_fine = st.number_input(
                "Fine Amount (₱)",
                min_value=0,
                step=100,
                value=int(v.get("Fine (₱)", 0) or 0),
            )
            new_license = st.text_input(
                "Driver License Number", value=v.get("License No.", "")
            )
            new_plate = st.text_input(
                "Plate Number (optional)", value=v.get("Plate No.", "") or ""
            )
        if st.form_submit_button("Save Changes", use_container_width=True):
            try:
                vioc.update_violation(
                    {
                        "top_number": v["TOP Number"],
                        "violation_type": new_type,
                        "violation_date": datetime.combine(new_date, new_time),
                        "location": new_location,
                        "apprehending_officer": new_officer,
                        "violation_status": new_status,
                        "fine_amount": int(new_fine),
                        "license_number": new_license.strip().upper(),
                        "plate_number": new_plate.strip().upper()
                        if new_plate.strip()
                        else None,
                    }
                )
                st.success("✅ Violation updated!")
                st.rerun()
            except Exception as e:
                st.error(f"Error updating record: {e}")


col_search, empty_space, col_filter, col_add = st.columns([4, 1.5, 1.5, 2])
with col_search:
    search_query = st.text_input(
        "Search",
        placeholder="Search by TOP number, type, location, license, or plate...",
        label_visibility="collapsed",
    )
with col_filter:
    if st.button("Filter", use_container_width=True):
        filter_dialog()
with col_add:
    if st.button("Add Violation", use_container_width=True):
        add_violation_dialog()

#  Active filter badge  #
f = st.session_state.vio_filters
_active_filters = []
if f.get("violation_status", "All Statuses") != "All Statuses":
    _active_filters.append(f"Status: {f['violation_status']}")
if f.get("violation_type", "All Types") != "All Types":
    _active_filters.append(f"Type: {f['violation_type']}")
if f.get("location_like"):
    _active_filters.append(f"Location: {f['location_like']}")
if f.get("date_mode", "Any Date") == "Single Year" and f.get("date_year"):
    _active_filters.append(f"Year: {f['date_year']}")
elif f.get("date_mode") == "Date Range" and f.get("date_from") and f.get("date_to"):
    _active_filters.append(f"Date: {f['date_from']} → {f['date_to']}")
if _active_filters:
    st.caption("🔍 Active filters: " + " | ".join(_active_filters))

try:
    violations = vioc.get_violations_by_criteria(
        {
            "violation_type": _vtype_to_backend(f["violation_type"]),
            "violation_status": _status_to_backend(f["violation_status"]),
            "location_like": f.get("location_like", ""),
            "date_from": f.get("date_from"),
            "date_to": f.get("date_to"),
        }
    )
except Exception as e:
    st.error(f"Error loading violations: {e}")
    violations = []

action_bar = st.empty()

if not violations:
    st.info("No violations found matching the current filters or search query.")
else:
    df = pd.DataFrame(violations)
    df.rename(
        columns={
            "violation_id": "violation_id",
            "top_number": "TOP Number",
            "violation_type": "Violation Type",
            "violation_date": "Date & Time",
            "location": "Location",
            "apprehending_officer": "Officer",
            "violation_status": "Status",
            "fine_amount": "Fine (₱)",
            "license_number": "License No.",
            "plate_number": "Plate No.",
        },
        inplace=True,
    )
    df["Plate No."] = df["Plate No."].fillna("—")

    if search_query:
        sq = search_query.lower()
        mask = (
            df["TOP Number"].str.lower().str.contains(sq, na=False)
            | df["Violation Type"].str.lower().str.contains(sq, na=False)
            | df["Location"].str.lower().str.contains(sq, na=False)
            | df["License No."].str.lower().str.contains(sq, na=False)
            | df["Plate No."].str.lower().str.contains(sq, na=False)
        )
        df = df[mask]

    if df.empty:
        st.info("No violations found matching the current filters or search query.")
    else:
        display_cols = [
            "TOP Number",
            "Violation Type",
            "Date & Time",
            "Location",
            "License No.",
            "Plate No.",
            "Fine (₱)",
            "Status",
            "Officer",
        ]
        full_cols = display_cols + ["violation_id"]
        df_full = df[[c for c in full_cols if c in df.columns]].copy()
        df_display = df[[c for c in display_cols if c in df.columns]].copy()

        paginated_display, start_idx, total_pages = paginate_df(
            df_display, "vio_page", rows_per_page=10
        )

        styler = paginated_display.style.format(
            {
                "Status": format_violation_status,
                "Fine (₱)": format_fine,
            }
        )
        styler = apply_styler(styler, color_violation_status, subset=["Status"])
        styled_df = styler.set_properties(
            **{"text-align": "center", "white-space": "pre-wrap"}
        )

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
                        if st.button(
                            "Delete",
                            type="primary",
                            use_container_width=True,
                            key="del_vio",
                        ):
                            delete_violation_dialog(full_row)
st.markdown("---")
with st.expander("📊 Report 6 — Violations by Type for a Given Year", expanded=False):
    st.markdown(
        "Counts all violations grouped by type for a selected calendar year. "
        "**Tip:** Use the **Filter** button above to narrow the main table by date range or city."
    )

    current_year = date.today().year
    r6_year = st.selectbox(
        "Select Year",
        options=list(range(current_year, current_year - 10, -1)),
        key="r6_year",
    )

    if st.button("Run Report", key="r6_run", type="primary"):
        try:
            start_dt = date(r6_year, 1, 1)
            end_dt = date(r6_year, 12, 31)
            results = vioc.get_violation_counts_by_type(start_dt, end_dt)

            if not results:
                st.info(f"No violations recorded in {r6_year}.")
            else:
                r6_df = (
                    pd.DataFrame(results)
                    .rename(
                        columns={
                            "violation_type": "Violation Type",
                            "total_violations": "Total Violations",
                        }
                    )
                    .sort_values("Total Violations", ascending=False)
                    .reset_index(drop=True)
                )
                col_chart, col_table = st.columns([3, 2])
                with col_chart:
                    st.bar_chart(
                        r6_df.set_index("Violation Type")["Total Violations"],
                        use_container_width=True,
                    )
                with col_table:
                    st.dataframe(r6_df, use_container_width=True, hide_index=True)
                st.caption(
                    f"Total violations recorded in **{r6_year}**: "
                    f"**{r6_df['Total Violations'].sum():,}**"
                )
        except Exception as e:
            st.error(f"Error running Report 6: {e}")


with st.expander("📍 Report 7 — Violations by City / Region", expanded=False):
    st.markdown(
        "Finds all violations whose location contains the search term (partial match). "
        "**Tip:** Use the **Filter** button above to apply this filter directly to the main table."
    )

    r7_location = st.text_input(
        "City or Region",
        placeholder="e.g. Quezon City, EDSA, Makati",
        key="r7_location",
    )

    if st.button("Run Report", key="r7_run", type="primary"):
        if not r7_location.strip():
            st.warning("Please enter a city or region name to search.")
        else:
            try:
                results = vioc.get_violations_by_location(r7_location.strip())

                if not results:
                    st.info(f"No violations found for location: **{r7_location}**")
                else:
                    r7_df = pd.DataFrame(results).rename(
                        columns={
                            "top_number": "TOP Number",
                            "violation_type": "Violation Type",
                            "violation_date": "Date & Time",
                            "location": "Location",
                            "apprehending_officer": "Officer",
                            "violation_status": "Status",
                            "fine_amount": "Fine (₱)",
                            "license_number": "License No.",
                            "plate_number": "Plate No.",
                        }
                    )
                    r7_df["Plate No."] = r7_df["Plate No."].fillna("—")

                    r7_display_cols = [
                        "TOP Number",
                        "Violation Type",
                        "Date & Time",
                        "Location",
                        "License No.",
                        "Plate No.",
                        "Fine (₱)",
                        "Status",
                    ]
                    r7_df = r7_df[[c for c in r7_display_cols if c in r7_df.columns]]

                    styler = r7_df.style.format(
                        {
                            "Status": format_violation_status,
                            "Fine (₱)": format_fine,
                        }
                    )
                    styler = apply_styler(
                        styler, color_violation_status, subset=["Status"]
                    )
                    styled = styler.set_properties(**{"text-align": "center"})

                    st.dataframe(styled, use_container_width=True, hide_index=True)
                    st.caption(
                        f"Found **{len(r7_df):,}** violation(s) in / near "
                        f"**{r7_location}**."
                    )
            except Exception as e:
                st.error(f"Error running Report 7: {e}")
