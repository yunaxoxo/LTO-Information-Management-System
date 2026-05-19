# Service layer for Traffic Violation database operations
# All queries use parameterized ? placeholders (mariadb positional binding)
import streamlit as st
from db.db_connection import execute_query
from db.query_helpers import build_dynamic_where


# ============================================================
# CREATE
# ============================================================

def record_new_traffic_violation(violation):
    """
    Inserts a new traffic violation record.
    NOTE: violation_id is AUTO_INCREMENT — do NOT insert it manually.
    """
    query = """
        INSERT INTO traffic_violations
            (top_number, violation_type, violation_date, location,
             apprehending_officer, violation_status, fine_amount,
             license_number, plate_number)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)"""
    params = (
        violation.top_number,
        violation.violation_type,
        violation.violation_date,
        violation.location,
        violation.apprehending_officer,
        violation.violation_status,
        violation.fine_amount,
        violation.license_number,
        violation.plate_number,
    )
    execute_query(query, params, fetch=False)
    st.cache_data.clear()
    return "Traffic violation recorded successfully."


# ============================================================
# READ
# ============================================================

@st.cache_data(ttl=300)
def fetch_traffic_violations_by_criteria(
    violation_type="ALL", violation_status="ALL",
    license_number="ALL", plate_number="ALL",
    location_like="", date_from=None, date_to=None,
):
    """
    Fetches traffic violations matching optional filter criteria.
    Supports equality filters (type, status, license, plate),
    a LIKE filter on location, and a date-range BETWEEN filter.
    """
    filters = {
        "violation_type": violation_type,
        "violation_status": violation_status,
        "license_number": license_number,
        "plate_number": plate_number,
    }
    column_map = {
        "violation_type": "violation_type",
        "violation_status": "violation_status",
        "license_number": "license_number",
        "plate_number": "plate_number",
    }
    where, params = build_dynamic_where(filters, column_map)
    params = list(params)

    if location_like and location_like.strip():
        where += " AND location LIKE CONCAT('%', ?, '%')"
        params.append(location_like.strip())

    if date_from and date_to:
        where += " AND violation_date BETWEEN ? AND ?"
        params.extend([str(date_from), str(date_to)])
    elif date_from:
        where += " AND violation_date >= ?"
        params.append(str(date_from))
    elif date_to:
        where += " AND violation_date <= ?"
        params.append(str(date_to))

    query = f"SELECT * FROM traffic_violations {where}"
    return execute_query(query, tuple(params))


@st.cache_data(ttl=300)
def fetch_violations_by_driver(license_number, start_date, end_date):
    """
    REPORT 5: View all traffic violations committed by a given driver
    within a specified date range.
    """
    query = """
        SELECT * FROM traffic_violations
        WHERE license_number = ?
        AND violation_date BETWEEN ? AND ?"""
    return execute_query(query, (license_number, start_date, end_date))


@st.cache_data(ttl=300)
def fetch_violation_counts_by_type(start_date, end_date):
    """
    REPORT 6: View the total number of violations per violation type
    for a given date range (typically a calendar year).
    """
    query = """
        SELECT violation_type, COUNT(*) AS total_violations
        FROM traffic_violations
        WHERE violation_date BETWEEN ? AND ?
        GROUP BY violation_type"""
    return execute_query(query, (start_date, end_date))


@st.cache_data(ttl=300)
def fetch_violations_by_location(location):
    """
    REPORT 7: View all vehicles involved in violations within a given
    city or region. Uses LIKE with wildcard matching.
    """
    query = """
        SELECT * FROM traffic_violations
        WHERE location LIKE CONCAT('%', ?, '%')"""
    return execute_query(query, (location,))


# ============================================================
# UPDATE
# ============================================================

def update_traffic_violation(violation):
    """Updates an existing traffic violation identified by top_number."""
    query = """
        UPDATE traffic_violations
        SET violation_type = ?, violation_date = ?, location = ?,
            apprehending_officer = ?, violation_status = ?,
            fine_amount = ?, license_number = ?, plate_number = ?
        WHERE top_number = ?"""
    params = (
        violation.violation_type,
        violation.violation_date,
        violation.location,
        violation.apprehending_officer,
        violation.violation_status,
        violation.fine_amount,
        violation.license_number,
        violation.plate_number,
        violation.top_number,
    )
    rows = execute_query(query, params, fetch=False)
    st.cache_data.clear()
    if rows == 0:
        return f"No violation found with TOP number '{violation.top_number}'."
    return "Traffic violation updated successfully."


# ============================================================
# DELETE
# ============================================================

def delete_traffic_violation(top_number):
    """Deletes a traffic violation by top_number."""
    query = "DELETE FROM traffic_violations WHERE top_number = ?"
    rows = execute_query(query, (top_number,), fetch=False)
    st.cache_data.clear()
    if rows == 0:
        return f"No violation found with TOP number '{top_number}'."
    return "Traffic violation deleted successfully."
