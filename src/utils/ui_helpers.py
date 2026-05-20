import math
from pathlib import Path
from typing import Any, Callable, Tuple

import pandas as pd
import streamlit as st


# ── CSS LOADER ────────────────────────────────────────────────────────
def css_style(current_file_path: str) -> None:
    """
    Bulletproof CSS loader. Points to css/style.css and handles font loads.
    """
    caller_path = Path(current_file_path).resolve()

    if caller_path.parent.name == "pages":
        root_dir = caller_path.parent.parent
    else:
        root_dir = caller_path.parent

    css_path = root_dir / "css" / "style.css"

    try:
        with open(css_path) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        st.warning(
            f"Could not locate CSS at {css_path}. Check your directory structure."
        )


# ── SIDEBAR & NAVIGATION ──────────────────────────────────────────────
def render_sidebar() -> None:
    """Hides native nav, injects brand header, custom icon nav, and bottom utility buttons."""
    st.markdown(
        "<style>[data-testid='stSidebarNav']{display:none!important;}</style>",
        unsafe_allow_html=True,
    )
    with st.sidebar:
        # Brand header
        st.markdown(
            """
            <div class="sidebar-brand">
                <div class="sidebar-brand-title">LTO Management System</div>
                <div class="sidebar-brand-sub">Land Transportation Office</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Custom navigation using Streamlit's native material icon styling
        st.page_link("Dashboard.py", label="Dashboard", icon=":material/dashboard:")
        st.page_link("pages/1_Drivers.py", label="Drivers", icon=":material/badge:")
        st.page_link(
            "pages/2_Vehicles.py", label="Vehicles", icon=":material/directions_car:"
        )
        st.page_link(
            "pages/3_Registrations.py",
            label="Registrations",
            icon=":material/assignment:",
        )
        st.page_link(
            "pages/4_Violations.py", label="Violations", icon=":material/warning:"
        )

        # ── REFACTORED BOTTOM UTILITIES ──────────────────────────────────
        # Fixed text-doubling by wrapping native page links inside a structural footer container.
        st.markdown('<div class="sidebar-bottom">', unsafe_allow_html=True)
        st.page_link("Dashboard.py", label="Settings", icon=":material/settings:")
        st.page_link("Dashboard.py", label="Support", icon=":material/help:")
        st.markdown("</div>", unsafe_allow_html=True)


# ── DASHBOARD METRICS ─────────────────────────────────────────────────
def metric_card(
    label: str, value: str, sub: str, color: str, sub_color: str = None
) -> str:
    """Returns an HTML metric card string with auto-adjusting font-sizes to prevent wrapping truncation."""
    sub_style = f"color: {sub_color};" if sub_color else "opacity: 0.7;"

    # Dynamically scales currency outputs down so they stay on a single line
    font_size = "1.5rem" if "₱" in value and len(value) > 8 else "1.8rem"

    return f"""
    <div style="padding:15px;border-radius:12px;border-top:5px solid {color};
                background-color: var(--secondary-background-color);
                color: var(--text-color);
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                border-left: 1px solid rgba(128,128,128,0.15);
                border-right: 1px solid rgba(128,128,128,0.15);
                border-bottom: 1px solid rgba(128,128,128,0.15);margin-bottom:0;">
        <p style="margin:0;font-size:11px;font-weight:600;text-transform:uppercase;opacity:0.6;color:var(--text-color);letter-spacing:0.05em;">{label}</p>
        <h2 style="margin:6px 0 0 0;font-size:{font_size};color:var(--text-color);font-weight:700;font-family:'JetBrains Mono', monospace;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">{value}</h2>
        <p style="margin:4px 0 0 0;font-size:13px;font-weight:500;{sub_style}">{sub}</p>
    </div>
    """


def safe_str(series: pd.Series) -> pd.Series:
    """Safe string conversion — replaces NaN/None with empty string."""
    return series.fillna("").astype(str).str.strip()


# ── NATIVE STREAMLIT PAGINATION ───────────────────────────────────────
def paginate_df(
    df: pd.DataFrame, page_key: str, rows_per_page: int = 10
) -> Tuple[pd.DataFrame, int, int]:
    """Slices the dataframe for the current page and clamps the page index safely."""
    total_pages = math.ceil(len(df) / rows_per_page) if len(df) > 0 else 1

    if st.session_state.get(page_key, 1) > total_pages:
        st.session_state[page_key] = total_pages
    if st.session_state.get(page_key, 1) < 1:
        st.session_state[page_key] = 1

    current_page = st.session_state.get(page_key, 1)
    start_idx = (current_page - 1) * rows_per_page
    end_idx = start_idx + rows_per_page

    return df.iloc[start_idx:end_idx], start_idx, total_pages


def render_pagination_controls(
    page_key: str, total_pages: int, paginated_df: pd.DataFrame
) -> None:
    """Renders sleek vector-based pagination controls beneath dataframes."""
    current_page = st.session_state.get(page_key, 1)
    pg_col1, pg_col2, pg_col3 = st.columns([1, 4, 1])

    with pg_col1:
        if st.button(
            ":material/arrow_back: Previous",
            disabled=(current_page == 1),
            use_container_width=True,
            key=f"{page_key}_prev",
        ):
            st.session_state[page_key] -= 1
            st.rerun()

    with pg_col2:
        st.markdown(
            f"<div style='text-align: center; color: var(--text-color); opacity: 0.7; padding-top: 8px;'>"
            f"Page <b>{current_page}</b> of <b>{total_pages}</b> "
            f"(Showing {len(paginated_df)} records)</div>",
            unsafe_allow_html=True,
        )

    with pg_col3:
        if st.button(
            "Next :material/arrow_forward:",
            disabled=(current_page == total_pages),
            use_container_width=True,
            key=f"{page_key}_next",
        ):
            st.session_state[page_key] += 1
            st.rerun()


# ── DATA FRAME STYLERS & FORMATTERS ───────────────────────────────────
def apply_styler(styler: Any, fn: Callable[[Any], str], subset: Any) -> Any:
    """Safely runs Styler mapping functions regardless of pandas version."""
    try:
        return styler.map(fn, subset=subset)
    except AttributeError:
        return styler.applymap(fn, subset=subset)


# ── LICENSE STATUS HIGHLIGHTS ──
def color_license_status(val: str) -> str:
    # Rich status highlights with 15% opacity backgrounds and round tags
    colors = {
        "Valid": "color: #22c55e; background-color: rgba(34, 197, 94, 0.15); border-radius: 4px;",
        "Expired": "color: #ef4444; background-color: rgba(239, 68, 68, 0.15); border-radius: 4px;",
        "Suspended": "color: #f59e0b; background-color: rgba(245, 158, 11, 0.15); border-radius: 4px;",
        "Revoked": "color: #9ca3af; background-color: rgba(156, 163, 175, 0.15); border-radius: 4px;",
    }
    return colors.get(val, "")


def format_license_status(val: str) -> str:
    return str(val).upper()


# ── LICENSE TYPE HIGHLIGHTS ──
def color_license_type(val: str) -> str:
    colors = {
        "Student": "color: #c084fc; background-color: rgba(192, 132, 252, 0.15); border-radius: 4px;",
        "Professional": "color: #60a5fa; background-color: rgba(96, 165, 250, 0.15); border-radius: 4px;",
        "Non-Professional": "color: #38bdf8; background-color: rgba(56, 189, 248, 0.15); border-radius: 4px;",
    }
    return colors.get(val, "")


def format_license_type(val: str) -> str:
    short = {
        "Non-Professional": "NON-PROF",
        "Professional": "PROFESSIONAL",
        "Student": "STUDENT",
    }
    return short.get(val, str(val).upper())


# ── REGISTRATION STATUS HIGHLIGHTS ──
def color_reg_status(val: str) -> str:
    colors = {
        "Active": "color: #22c55e; background-color: rgba(34, 197, 94, 0.15); border-radius: 4px;",
        "Expired": "color: #ef4444; background-color: rgba(239, 68, 68, 0.15); border-radius: 4px;",
        "Suspended": "color: #f59e0b; background-color: rgba(245, 158, 11, 0.15); border-radius: 4px;",
    }
    return colors.get(val, "")


def format_reg_status(val: str) -> str:
    return str(val).upper()


# ── VIOLATION STATUS HIGHLIGHTS ──
def color_violation_status(val: str) -> str:
    colors = {
        "Paid": "color: #22c55e; background-color: rgba(34, 197, 94, 0.15); border-radius: 4px;",
        "Unpaid": "color: #ef4444; background-color: rgba(239, 68, 68, 0.15); border-radius: 4px;",
        "Contested": "color: #f59e0b; background-color: rgba(245, 158, 11, 0.15); border-radius: 4px;",
    }
    return colors.get(val, "")


def format_violation_status(val: str) -> str:
    return str(val).upper()


# ── VEHICLE TYPE HIGHLIGHTS ──
def color_vehicle_type(val: str) -> str:
    palette = {
        "Sedan": "color: #60a5fa; background-color: rgba(96, 165, 250, 0.12);",
        "SUV": "color: #4ade80; background-color: rgba(74, 222, 128, 0.12);",
        "Hatchback": "color: #c084fc; background-color: rgba(192, 132, 252, 0.12);",
        "MPV": "color: #facc15; background-color: rgba(250, 204, 21, 0.12);",
        "Pickup": "color: #fb923c; background-color: rgba(251, 146, 60, 0.12);",
        "Van": "color: #9ca3af; background-color: rgba(156, 163, 175, 0.12);",
        "Coupe": "color: #f43f5e; background-color: rgba(244, 63, 94, 0.12);",
        "Convertible": "color: #f472b6; background-color: rgba(244, 114, 182, 0.12);",
        "Commercial Truck": "color: #22d3ee; background-color: rgba(34, 211, 238, 0.12);",
        "Bus": "color: #2dd4bf; background-color: rgba(45, 212, 191, 0.12);",
        "Light Truck": "color: #a3e635; background-color: rgba(163, 230, 53, 0.12);",
    }
    return (
        palette.get(val, "color: #9ca3af; background-color: rgba(156, 163, 175, 0.12);")
        + " border-radius: 4px;"
    )


def format_fine(val: Any) -> str:
    try:
        return f"₱{int(val):,}"
    except (ValueError, TypeError):
        return str(val)


def render_dataframe(
    styler: Any, selection_mode: str = "single-row", on_select: str = "rerun"
) -> Any:
    """
    Universally styles any pandas Styler or DataFrame with bold JetBrains Mono,
    and returns a native Streamlit dataframe object.
    """
    # If a raw DataFrame is passed, convert it to a Styler first
    if hasattr(styler, "to_frame"):
        styler = styler.style

    # Bypasses Canvas protection by injecting font declarations inline
    styled_df = styler.set_properties(
        **{
            "font-family": "JetBrains Mono, monospace",
            "font-weight": "500",
            "font-size": "13px",
        }
    )

    return st.dataframe(
        styled_df,
        use_container_width=True,
        hide_index=True,
        on_select=on_select,
        selection_mode=selection_mode,
    )
