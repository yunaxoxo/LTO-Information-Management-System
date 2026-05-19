from pathlib import Path
import math
import pandas as pd
import streamlit as st


# ---------------------- CSS LOADER ---------------------- #
# loads the stylesheet relative to the calling page file
def css_style(caller_file: str, style: str = "style.css") -> None:
    try:
        css_path = Path(caller_file).parent.parent / "css" / style
        with open(css_path, "r") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        st.error(f"Couldn't find CSS file at: {css_path}")

# ---------------------- END OF CSS LOADER ---------------------- #


# ---------------------- DATAFRAME UTILITIES ---------------------- #
# safe string conversion — replaces NaN/None with empty string before concat
def safe_str(series: pd.Series) -> pd.Series:
    return series.fillna("").astype(str).str.strip()

# ---------------------- END OF DATAFRAME UTILITIES ---------------------- #


# ---------------------- PAGINATION ---------------------- #
# slices the dataframe for the current page and clamps the page index
def paginate_df(df: pd.DataFrame, page_key: str, rows_per_page: int = 10):
    total_pages = math.ceil(len(df) / rows_per_page) if len(df) > 0 else 1

    # clamp page within valid range
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
            f"<div style='text-align: center; color: #64748b; padding-top: 8px;'>"
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


# ---------------------- STYLER COMPATIBILITY WRAPPER ---------------------- #
# handles .map vs .applymap depending on the installed pandas version
def apply_styler(styler, fn, subset):
    try:
        return styler.map(fn, subset=subset)
    except AttributeError:
        return styler.applymap(fn, subset=subset)

# ---------------------- END OF STYLER COMPATIBILITY WRAPPER ---------------------- #


# ---------------------- PLATE NUMBER STYLE ---------------------- #
# dark license-plate badge — white bold text on a near-black background
def style_plate(val) -> str:
    return (
        "background-color: #1e293b; color: #f8fafc; font-weight: 700; "
        "border-radius: 4px; padding: 4px 8px; letter-spacing: 0.05em;"
    )

# ---------------------- END OF PLATE NUMBER STYLE ---------------------- #


# ---------------------- DRIVER LICENSE STATUS ---------------------- #
# color and icon formatters for Valid / Expired / Suspended / Revoked
def color_license_status(val: str) -> str:
    colors = {
        "Valid":     "color: #15803d; background-color: #dcfce7;",
        "Expired":   "color: #b91c1c; background-color: #fee2e2;",
        "Suspended": "color: #c2410c; background-color: #ffedd5;",
        "Revoked":   "color: #374151; background-color: #f3f4f6;",
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

# ---------------------- END OF DRIVER LICENSE STATUS ---------------------- #


# ---------------------- DRIVER LICENSE TYPE ---------------------- #
# color and text formatters for Student / Non-Professional / Professional
def color_license_type(val: str) -> str:
    colors = {
        "Student":          "color: #7e22ce; background-color: #f3e8ff;",
        "Professional":     "color: #ffffff; background-color: #1e3a8a;",
        "Non-Professional": "color: #0369a1; background-color: #e0f2fe;",
    }
    return colors.get(val, "")


def format_license_type(val: str) -> str:
    short = {
        "Non-Professional": "NON-PROFESSIONAL",
        "Professional":     "PROFESSIONAL",
        "Student":          "STUDENT",
    }
    return short.get(val, str(val).upper())

# ---------------------- END OF DRIVER LICENSE TYPE ---------------------- #


# ---------------------- REGISTRATION STATUS ---------------------- #
# color and icon formatters for Active / Expired / Suspended
def color_reg_status(val: str) -> str:
    colors = {
        "Active":    "color: #15803d; background-color: #dcfce7;",
        "Expired":   "color: #b91c1c; background-color: #fee2e2;",
        "Suspended": "color: #c2410c; background-color: #ffedd5;",
    }
    return colors.get(val, "")


def format_reg_status(val: str) -> str:
    icons = {"Active": "🟢 Active", "Expired": "🔴 Expired", "Suspended": "🟠 Suspended"}
    return icons.get(val, val)

# ---------------------- END OF REGISTRATION STATUS ---------------------- #


# ---------------------- VIOLATION STATUS ---------------------- #
# color and icon formatters for Paid / Unpaid / Contested
def color_violation_status(val: str) -> str:
    colors = {
        "Paid":      "color: #15803d; background-color: #dcfce7;",
        "Unpaid":    "color: #b91c1c; background-color: #fee2e2;",
        "Contested": "color: #c2410c; background-color: #ffedd5;",
    }
    return colors.get(val, "")


def format_violation_status(val: str) -> str:
    icons = {"Paid": "🟢 Paid", "Unpaid": "🔴 Unpaid", "Contested": "🟠 Contested"}
    return icons.get(val, val)

# ---------------------- END OF VIOLATION STATUS ---------------------- #


# ---------------------- VEHICLE TYPE ---------------------- #
# color badges for the 11 supported vehicle categories
def color_vehicle_type(val: str) -> str:
    palette = {
        "Sedan":            "color: #1e40af; background-color: #dbeafe;",
        "SUV":              "color: #065f46; background-color: #d1fae5;",
        "Hatchback":        "color: #7e22ce; background-color: #f3e8ff;",
        "MPV":              "color: #c2410c; background-color: #ffedd5;",
        "Pickup":           "color: #854d0e; background-color: #fef9c3;",
        "Van":              "color: #374151; background-color: #f3f4f6;",
        "Coupe":            "color: #9f1239; background-color: #ffe4e6;",
        "Convertible":      "color: #be185d; background-color: #fce7f3;",
        "Commercial Truck": "color: #1e3a5f; background-color: #bfdbfe;",
        "Bus":              "color: #166534; background-color: #bbf7d0;",
        "Light Truck":      "color: #4d7c0f; background-color: #ecfccb;",
    }
    return palette.get(val, "color: #374151; background-color: #f3f4f6;")

# ---------------------- END OF VEHICLE TYPE ---------------------- #


# ---------------------- FINE FORMATTER ---------------------- #
# formats integer fine amounts as Philippine Peso with comma separators
def format_fine(val) -> str:
    try:
        return f"₱{int(val):,}"
    except (ValueError, TypeError):
        return str(val)

# ---------------------- END OF FINE FORMATTER ---------------------- #
