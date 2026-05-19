# Service layer for Driver-related database operations
# All queries use parameterized ? placeholders (mariadb positional binding)
import streamlit as st
from db.db_connection import execute_query
from db.query_helpers import build_dynamic_where


# ============================================================
# CREATE
# ============================================================

def register_new_driver(driver):
    """Inserts a new driver record into the database."""
    query = """
        INSERT INTO drivers
            (license_number, full_name, birthday, sex, address,
             license_type, license_status, license_issuance_date, license_expiration_date)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)"""
    params = (
        driver.license_number,
        driver.full_name,
        driver.birthday,
        driver.sex,
        driver.address,
        driver.license_type,
        driver.license_status,
        driver.license_issuance_date,
        driver.license_expiration_date,
    )
    execute_query(query, params, fetch=False)
    st.cache_data.clear()
    return "Driver registered successfully."


# ============================================================
# READ
# ============================================================

@st.cache_data(ttl=300)
def fetch_drivers_by_criteria(
    license_type="ALL", license_status="ALL", sex="ALL", min_age=None, max_age=None
):
    """
    REPORT 1: View all registered drivers filtered by license type,
    license status, sex, and age range.

    Uses the DRY dynamic WHERE builder for the standard equality filters,
    then appends the age-range condition separately (since it uses TIMESTAMPDIFF).
    """
    filters = {
        "license_type": license_type,
        "license_status": license_status,
        "sex": sex,
    }
    column_map = {
        "license_type": "license_type",
        "license_status": "license_status",
        "sex": "sex",
    }

    where, params = build_dynamic_where(filters, column_map)

    # Age range filter (only applied when both min_age and max_age are provided)
    if min_age is not None and max_age is not None:
        where += " AND TIMESTAMPDIFF(YEAR, birthday, CURDATE()) BETWEEN ? AND ?"
        params = params + (int(min_age), int(max_age))

    query = f"SELECT * FROM drivers {where}"
    return execute_query(query, params)


@st.cache_data(ttl=300)
def fetch_invalid_licenses():
    """
    REPORT 4: View all drivers with expired or suspended licenses.
    """
    query = "SELECT * FROM drivers WHERE license_status IN ('Expired', 'Suspended')"
    return execute_query(query)


# ============================================================
# UPDATE
# ============================================================

def update_driver_info(driver):
    """Updates an existing driver record identified by license_number."""
    query = """
        UPDATE drivers
        SET full_name = ?, birthday = ?, sex = ?, address = ?,
            license_type = ?, license_status = ?,
            license_issuance_date = ?, license_expiration_date = ?
        WHERE license_number = ?"""
    params = (
        driver.full_name,
        driver.birthday,
        driver.sex,
        driver.address,
        driver.license_type,
        driver.license_status,
        driver.license_issuance_date,
        driver.license_expiration_date,
        driver.license_number,
    )
    rows = execute_query(query, params, fetch=False)
    st.cache_data.clear()
    if rows == 0:
        return f"No driver found with license number '{driver.license_number}'."
    return "Driver information updated successfully."


# ============================================================
# DELETE
# ============================================================

def delete_driver(license_number):
    """Deletes a driver record by license_number."""
    query = "DELETE FROM drivers WHERE license_number = ?"
    rows = execute_query(query, (license_number,), fetch=False)
    st.cache_data.clear()
    if rows == 0:
        return f"No driver found with license number '{license_number}'."
    return "Driver deleted successfully."
