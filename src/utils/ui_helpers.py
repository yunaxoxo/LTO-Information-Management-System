from pathlib import Path
import math
import pandas as pd
import streamlit as st

def css_style(current_file_path):
    """
    Bulletproof CSS loader. Dynamically finds the root src/ directory 
    and points to css/style.css regardless of which page calls it.
    """
    # Gets the directory of the file calling this function, then navigates to root / src
    src_dir = Path(__file__).resolve().parent.parent 
    css_path = src_dir / "css" / "style.css"
    
    try:
        with open(css_path) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        st.warning(f"Could not locate CSS at {css_path}. Check your directory structure.")


def render_sidebar():
    """Hides native nav, injects brand header at top, custom icon nav, and bottom utility buttons."""
    # Globally hide the native Streamlit page navigation
    st.markdown(
        "<style>[data-testid='stSidebarNav']{display:none!important;}</style>",
        unsafe_allow_html=True,
    )
    with st.sidebar:
        # ── Brand header ─────────────────────────────────────────────────────
        st.markdown(
            """
            <div class="sidebar-brand">
                <div class="sidebar-brand-title">🚗 LTO Management System</div>
                <div class="sidebar-brand-sub">Land Transportation Office</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        # ── Custom navigation with icons ──────────────────────────────────────
        st.page_link("Dashboard.py",           label="📊  Dashboard")
        st.page_link("pages/1_Drivers.py",     label="👤  Drivers")
        st.page_link("pages/2_Vehicles.py",    label="🚗  Vehicles")
        st.page_link("pages/3_Registrations.py", label="📋  Registrations")
        st.page_link("pages/4_Violations.py",  label="⚠️  Violations")
        # ── Bottom utility buttons ────────────────────────────────────────────
        st.markdown(
            """
            <div class="sidebar-bottom">
                <div class="sidebar-bottom-btn">⚙️&nbsp; Settings</div>
                <div class="sidebar-bottom-btn">❓&nbsp; Support</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def metric_card(label: str, value: str, sub: str, color: str, sub_color: str = None) -> str:
    """Returns an HTML metric card string matching the Dashboard style."""
    sub_style = f"color: {sub_color};" if sub_color else "opacity: 0.7;"
    return f"""
    <div style="padding:15px;border-radius:8px;border-top:5px solid {color};
                background-color: var(--secondary-background-color);
                color: var(--text-color);
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                border-left: 1px solid rgba(128,128,128,0.2);
                border-right: 1px solid rgba(128,128,128,0.2);
                border-bottom: 1px solid rgba(128,128,128,0.2);margin-bottom:0;">
        <p style="margin:0;font-size:12px;font-weight:600;text-transform:uppercase;opacity:0.7;color:var(--text-color);">{label}</p>
        <h2 style="margin:5px 0 0 0;font-size:2.0rem;color:var(--text-color);font-weight:700;">{value}</h2>
        <p style="margin:5px 0 0 0;font-size:13px;font-weight:600;{sub_style}">{sub}</p>
    </div>
    """


# safe string conversion — replaces NaN/None with empty string 
def safe_str(series: pd.Series) -> pd.Series:
    return series.fillna("").astype(str).str.strip()


# ---------------------- PAGINATION ---------------------- #
# slices the dataframe for the current page and clamps the page index
def paginate_df(df: pd.DataFrame, page_key: str, rows_per_page: int = 10):
    total_pages = math.ceil(len(df) / rows_per_page) if len(df) > 0 else 1

    # ensure that page stays within range
    if st.session_state.get(page_key, 1) > total_pages:
        st.session_state[page_key] = total_pages
    if st.session_state.get(page_key, 1) < 1:
        st.session_state[page_key] = 1

    current_page = st.session_state.get(page_key, 1)
    start_idx = (current_page - 1) * rows_per_page
    end_idx = start_idx + rows_per_page

    return df.iloc[start_idx:end_idx], start_idx, total_pages


# renders previous / page info / next buttons below the table
def render_pagination_controls(page_key: str, total_pages: int, paginated_df: pd.DataFrame) -> None:
    current_page = st.session_state.get(page_key, 1)
    pg_col1, pg_col2, pg_col3 = st.columns([1, 4, 1])

    # previous button
    with pg_col1:
        if st.button("⬅️ Previous", disabled=(current_page == 1),
                     use_container_width=True, key=f"{page_key}_prev"):
            st.session_state[page_key] -= 1
            st.rerun()

    with pg_col2:
        st.markdown(
            f"<div style='text-align: center; color: var(--text-color); opacity: 0.7; padding-top: 8px;'>"
            f"Page <b>{current_page}</b> of <b>{total_pages}</b> "
            f"(Showing {len(paginated_df)} records)</div>",
            unsafe_allow_html=True,
        )

    # next button
    with pg_col3:
        if st.button("Next ➡️", disabled=(current_page == total_pages),
                     use_container_width=True, key=f"{page_key}_next"):
            st.session_state[page_key] += 1
            st.rerun()

# ---------------------- END OF PAGINATION ---------------------- #

def apply_styler(styler, fn, subset):
    try:
        return styler.map(fn, subset=subset)
    except AttributeError:
        return styler.applymap(fn, subset=subset)


# color and icon formatters for Valid / Expired / Suspended / Revoked
def color_license_status(val: str) -> str:
    colors = {
        "Valid":     "color:#16a34a; background-color:rgba(22,163,74,0.15);  font-weight:600;",
        "Expired":   "color:#dc2626; background-color:rgba(220,38,38,0.15);  font-weight:600;",
        "Suspended": "color:#d97706; background-color:rgba(217,119,6,0.15);  font-weight:600;",
        "Revoked":   "color:#6b7280; background-color:rgba(107,114,128,0.15);font-weight:600;",
    }
    return colors.get(val, "")


def format_license_status(val: str) -> str:
    icons = {
        "Valid":     "🟢 Valid",
        "Expired":   "🔴 Expired",
        "Suspended": "🟠 Suspended",
        "Revoked":   "⚪ Revoked",
    }
    return icons.get(val, val)


# color and text formatters for Student / Non-Professional / Professional
def color_license_type(val: str) -> str:
    colors = {
        "Student":          "color:#9333ea; background-color:rgba(147,51,234,0.15); font-weight:700;",
        "Professional":     "color:#2563eb; background-color:rgba(37,99,235,0.15);  font-weight:700;",
        "Non-Professional": "color:#0284c7; background-color:rgba(2,132,199,0.15);  font-weight:700;",
    }
    return colors.get(val, "")


def format_license_type(val: str) -> str:
    short = {
        "Non-Professional": "NON-PROFESSIONAL",
        "Professional":     "PROFESSIONAL",
        "Student":          "STUDENT",
    }
    return short.get(val, str(val).upper())

# color and icon formatters for Active / Expired / Suspended
def color_reg_status(val: str) -> str:
    colors = {
        "Active":    "color:#16a34a; background-color:rgba(22,163,74,0.15); font-weight:600;",
        "Expired":   "color:#dc2626; background-color:rgba(220,38,38,0.15); font-weight:600;",
        "Suspended": "color:#d97706; background-color:rgba(217,119,6,0.15); font-weight:600;",
    }
    return colors.get(val, "")


def format_reg_status(val: str) -> str:
    icons = {"Active": "🟢 Active", "Expired": "🔴 Expired", "Suspended": "🟠 Suspended"}
    return icons.get(val, val)

# color and icon formatters for Paid / Unpaid / Contested
def color_violation_status(val: str) -> str:
    colors = {
        "Paid":      "color:#16a34a; background-color:rgba(22,163,74,0.15); font-weight:600;",
        "Unpaid":    "color:#dc2626; background-color:rgba(220,38,38,0.15); font-weight:600;",
        "Contested": "color:#d97706; background-color:rgba(217,119,6,0.15); font-weight:600;",
    }
    return colors.get(val, "")


def format_violation_status(val: str) -> str:
    icons = {"Paid": "🟢 Paid", "Unpaid": "🔴 Unpaid", "Contested": "🟠 Contested"}
    return icons.get(val, val)

# color badges for the 11 supported vehicle categories
def color_vehicle_type(val: str) -> str:
    palette = {
        "Sedan":            "color:#2563eb; background-color:rgba(37,99,235,0.15);",
        "SUV":              "color:#16a34a; background-color:rgba(22,163,74,0.15);",
        "Hatchback":        "color:#9333ea; background-color:rgba(147,51,234,0.15);",
        "MPV":              "color:#ca8a04; background-color:rgba(202,138,4,0.15);",
        "Pickup":           "color:#ca8a04; background-color:rgba(202,138,4,0.15);",
        "Van":              "color:#4b5563; background-color:rgba(75,85,99,0.15);",
        "Coupe":            "color:#e11d48; background-color:rgba(225,29,72,0.15);",
        "Convertible":      "color:#db2777; background-color:rgba(219,39,119,0.15);",
        "Commercial Truck": "color:#0891b2; background-color:rgba(8,145,178,0.15);",
        "Bus":              "color:#059669; background-color:rgba(5,150,105,0.15);",
        "Light Truck":      "color:#65a30d; background-color:rgba(101,163,13,0.15);",
    }
    return palette.get(val, "color:#4b5563; background-color:rgba(75,85,99,0.15);")

# formats integer fine amounts as Philippine Peso
def format_fine(val) -> str:
    try:
        return f"₱{int(val):,}"
    except (ValueError, TypeError):
        return str(val)