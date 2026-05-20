from datetime import date
import pandas as pd
import streamlit as st
from controllers import registration_controller as rc
from services import dashboard_service as dash_srv
from utils.ui_helpers import (
    css_style, render_sidebar, metric_card,
    paginate_df, render_pagination_controls,
    apply_styler,
    color_reg_status, format_reg_status,
)

st.set_page_config(page_title="Vehicle Registrations", layout="wide")
css_style(__file__)
render_sidebar()
_header = st.empty()  # filled after dialogs are defined (below)

# ── Metric cards ──
@st.cache_data(ttl=60)
def _reg_metrics():
    return {
        "total":    dash_srv.get_total_registrations_count(),
        "active":   dash_srv.get_active_registrations(),
        "expired":  dash_srv.get_expired_registrations_count(),
        "expiring": dash_srv.get_expiring_registrations_count(),
    }

_rm = _reg_metrics()
m1, m2, m3, m4 = st.columns(4)
with m1:
    st.markdown(metric_card("📋 Total Registrations", f"{_rm['total']:,}", "All records", "#1f77b4"), unsafe_allow_html=True)
with m2:
    st.markdown(metric_card("✅ Active", f"{_rm['active']:,}", "Currently valid", "#2e8b57"), unsafe_allow_html=True)
with m3:
    st.markdown(metric_card("🔴 Expired", f"{_rm['expired']:,}", "Past expiration date", "#d62728"), unsafe_allow_html=True)
with m4:
    st.markdown(metric_card("⏰ Expiring Soon", f"{_rm['expiring']:,}", "Within 30 days", "#ff7f0e"), unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)
st.markdown("---")

#  Filter option constants  #
STATUS_FILTER_OPTIONS = ["All Statuses", "Active", "Expired", "Suspended"]
STATUS_OPTS           = [s for s in STATUS_FILTER_OPTIONS if s != "All Statuses"]

#  Session state  #
if "reg_filters" not in st.session_state:
    st.session_state.reg_filters = {
        "registration_status": "All Statuses",  
        "plate_number":        "",               
    }
if "reg_page" not in st.session_state:
    st.session_state.reg_page = 1

def _status_to_backend(label: str) -> str:
    return "ALL" if label == "All Statuses" else label

#  DIALOGS  #

@st.dialog("Filter Registrations")
def filter_dialog():
    st.write("Narrow results by registration status or plate number:")
    cur = st.session_state.reg_filters
    stat_idx = STATUS_FILTER_OPTIONS.index(cur["registration_status"]) \
               if cur["registration_status"] in STATUS_FILTER_OPTIONS else 0

    registration_status = st.selectbox("Registration Status", STATUS_FILTER_OPTIONS, index=stat_idx)
    plate_number        = st.text_input(
        "Plate Number (exact match)", value=cur["plate_number"],
        placeholder="Leave empty for all"
    )

    if st.button("Apply Filters", use_container_width=True, type="primary"):
        st.session_state.reg_filters.update({
            "registration_status": registration_status,
            "plate_number":        plate_number.strip().upper(),
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
            reg_status = st.selectbox("Registration Status *", STATUS_OPTS)
        if st.form_submit_button("Add Registration", use_container_width=True, type="primary"):
            if not reg_number or not plate_number:
                st.error("Registration number and plate number are required.")
            elif exp_date <= reg_date:
                st.error("Expiration date must be after the registration date.")
            else:
                try:
                    rc.create_vehicle_registration({
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
    stat_idx = STATUS_OPTS.index(r["Status"]) if r.get("Status") in STATUS_OPTS else 0
    with st.form("edit_registration_form"):
        col1, col2 = st.columns(2)
        with col1:
            st.text_input("Registration No. (read-only)", value=r["Registration No."], disabled=True)
            new_plate    = st.text_input("Plate Number", value=r.get("Plate Number", ""))
            new_reg_date = st.date_input(
                "Registration Date",
                value=r["Registration Date"] if isinstance(r.get("Registration Date"), date) else date.today()
            )
        with col2:
            new_exp_date = st.date_input(
                "Expiration Date",
                value=r["Expiration Date"] if isinstance(r.get("Expiration Date"), date) else date.today()
            )
            new_status = st.selectbox("Status", STATUS_OPTS, index=stat_idx)
        if st.form_submit_button("Save Changes", use_container_width=True):
            if new_exp_date <= new_reg_date:
                st.error("Expiration date must be after the registration date.")
            else:
                try:
                    rc.update_registration({
                        "registration_number": r["Registration No."],
                        "registration_date":   new_reg_date,
                        "expiration_date":     new_exp_date,
                        "registration_status": new_status,
                        "plate_number":        new_plate.strip().upper(),
                    })
                    st.success("✅ Registration updated!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error updating record: {e}")


# ── Header row: title + action buttons (fills _header placeholder at top) ──
with _header.container():
    _ht, _hs, _hf, _ha = st.columns([4, 3.5, 1.2, 1.5])
    with _ht:
        st.title("Vehicle Registrations")
        st.caption("Manage and track vehicle registration records, validity periods, and registration status.")
    with _hs:
        st.markdown("<br>", unsafe_allow_html=True)
        search_query = st.text_input(
            "Search", placeholder="Search by registration number or plate number...",
            label_visibility="collapsed"
        )
    with _hf:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Filter", use_container_width=True):
            filter_dialog()
    with _ha:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Add Registration", use_container_width=True):
            add_registration_dialog()


#  Fetch data  #
f = st.session_state.reg_filters
try:
    registrations = rc.get_registrations_by_criteria({
        "registration_status": _status_to_backend(f["registration_status"]),
        "plate_number":        f["plate_number"] or "ALL",
    })
except Exception as e:
    st.error(f"Error loading registrations: {e}")
    registrations = []

action_bar = st.empty()

#  Build dataframe  #
if not registrations:
    st.info("No registrations found matching the current filters or search query.")
else:
    df = pd.DataFrame(registrations)

    rename_map = {
        "registration_number": "Registration No.",
        "plate_number":        "Plate Number",
        "registration_date":   "Registration Date",
        "expiration_date":     "Expiration Date",
        "registration_status": "Status",
    }
    df.rename(columns=rename_map, inplace=True)

    display_cols = [
        "Registration No.", "Plate Number",
        "Registration Date", "Expiration Date", "Status",
    ]
    df = df[[c for c in display_cols if c in df.columns]]

    if search_query:
        sq = search_query.lower()
        mask = (
            df["Registration No."].str.lower().str.contains(sq, na=False) |
            df["Plate Number"].str.lower().str.contains(sq, na=False)
        )
        df = df[mask]

    if df.empty:
        st.info("No registrations found matching the current filters or search query.")
    else:
        paginated_df, start_idx, total_pages = paginate_df(df, "reg_page", rows_per_page=10)

        styler = paginated_df.style.format({"Status": format_reg_status})
        styler = apply_styler(styler, color_reg_status, subset=["Status"])
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