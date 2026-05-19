# Service layer for Vehicle Registration database operations
# All queries use parameterized ? placeholders (mariadb positional binding)
import streamlit as st
from db.db_connection import execute_query
from db.query_helpers import build_dynamic_where


# ============================================================
# CREATE
# ============================================================

def register_new_vehicle_registration(registration):
    """Inserts a new vehicle registration record."""
    query = """
        INSERT INTO vehicle_registrations
            (registration_number, registration_date, expiration_date,
             registration_status, plate_number)
        VALUES (?, ?, ?, ?, ?)"""
    params = (
        registration.registration_number,
        registration.registration_date,
        registration.expiration_date,
        registration.registration_status,
        registration.plate_number,
    )
    execute_query(query, params, fetch=False)
    st.cache_data.clear()
    return "Vehicle registration created successfully."


# ============================================================
# READ
# ============================================================

@st.cache_data(ttl=300)
def fetch_vehicle_registrations_by_criteria(
    registration_status="ALL", plate_number="ALL"
):
    """
    Fetches vehicle registrations matching optional filter criteria.
    Only practical filter columns are exposed (status and plate_number).
    """
    filters = {
        "registration_status": registration_status,
        "plate_number": plate_number,
    }
    column_map = {
        "registration_status": "registration_status",
        "plate_number": "plate_number",
    }
    where, params = build_dynamic_where(filters, column_map)
    query = f"SELECT * FROM vehicle_registrations {where}"
    return execute_query(query, params)


# ============================================================
# UPDATE
# ============================================================

def update_vehicle_registration(registration):
    """Updates an existing vehicle registration identified by registration_number."""
    query = """
        UPDATE vehicle_registrations
        SET registration_date = ?, expiration_date = ?,
            registration_status = ?, plate_number = ?
        WHERE registration_number = ?"""
    params = (
        registration.registration_date,
        registration.expiration_date,
        registration.registration_status,
        registration.plate_number,
        registration.registration_number,
    )
    rows = execute_query(query, params, fetch=False)
    st.cache_data.clear()
    if rows == 0:
        return f"No registration found with number '{registration.registration_number}'."
    return "Vehicle registration updated successfully."


# ============================================================
# DELETE
# ============================================================

def delete_vehicle_registration(registration_number):
    """Deletes a vehicle registration by registration_number."""
    query = "DELETE FROM vehicle_registrations WHERE registration_number = ?"
    rows = execute_query(query, (registration_number,), fetch=False)
    st.cache_data.clear()
    if rows == 0:
        return f"No registration found with number '{registration_number}'."
    return "Vehicle registration deleted successfully."
