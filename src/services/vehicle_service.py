# Service layer for Vehicle-related database operations
# All queries use parameterized ? placeholders (mariadb positional binding)
import streamlit as st
from db.db_connection import execute_query
from db.query_helpers import build_dynamic_where


# ============================================================
# CREATE
# ============================================================


def register_new_vehicle(vehicle):
    """Inserts a new vehicle record into the database."""
    query = """
        INSERT INTO vehicles
            (plate_number, engine_number, chassis_number, make, model,
             year, color, vehicle_type, license_number)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)"""
    params = (
        vehicle.plate_number,
        vehicle.engine_number,
        vehicle.chassis_number,
        vehicle.make,
        vehicle.model,
        vehicle.year,
        vehicle.color,
        vehicle.vehicle_type,
        vehicle.license_number,
    )
    execute_query(query, params, fetch=False)
    st.cache_data.clear()
    return "Vehicle registered successfully."


# ============================================================
# READ
# ============================================================


@st.cache_data(ttl=300)
def fetch_vehicles_by_criteria(
    make="ALL",
    model="ALL",
    year="ALL",
    color="ALL",
    vehicle_type="ALL",
    license_number="ALL",
):
    """
    Fetches vehicles matching optional filter criteria.
    Uses the DRY dynamic WHERE builder.
    """
    filters = {
        "make": make,
        "model": model,
        "year": year,
        "color": color,
        "vehicle_type": vehicle_type,
        "license_number": license_number,
    }
    column_map = {
        "make": "make",
        "model": "model",
        "year": "year",
        "color": "color",
        "vehicle_type": "vehicle_type",
        "license_number": "license_number",
    }
    where, params = build_dynamic_where(filters, column_map)
    query = f"SELECT * FROM vehicles {where}"
    return execute_query(query, params)


@st.cache_data(ttl=300)
def fetch_vehicles_by_owner(license_number):
    """
    REPORT 2: View all vehicles owned by a given driver.
    """
    query = "SELECT * FROM vehicles WHERE license_number = ?"
    return execute_query(query, (license_number,))


@st.cache_data(ttl=300)
def fetch_expired_registrations(as_of_date):
    """
    REPORT 3: View all vehicles with expired registrations as of a given date.
    Joins vehicles with vehicle_registrations and checks expiration_date < as_of_date.
    """
    query = """
        SELECT v.plate_number, v.engine_number, v.chassis_number,
               v.make, v.model, v.year, v.color, v.vehicle_type, v.license_number,
               r.registration_number, r.registration_date,
               r.expiration_date, r.registration_status
        FROM vehicles v
        JOIN vehicle_registrations r ON v.plate_number = r.plate_number
        WHERE r.expiration_date < ?"""
    return execute_query(query, (as_of_date,))


# ============================================================
# UPDATE
# ============================================================


def update_vehicle_info(vehicle):
    """Updates an existing vehicle record identified by plate_number."""
    query = """
        UPDATE vehicles
        SET engine_number = ?, chassis_number = ?, make = ?, model = ?,
            year = ?, color = ?, vehicle_type = ?, license_number = ?
        WHERE plate_number = ?"""
    params = (
        vehicle.engine_number,
        vehicle.chassis_number,
        vehicle.make,
        vehicle.model,
        vehicle.year,
        vehicle.color,
        vehicle.vehicle_type,
        vehicle.license_number,
        vehicle.plate_number,
    )
    rows = execute_query(query, params, fetch=False)
    st.cache_data.clear()
    if rows == 0:
        return f"No vehicle found with plate number '{vehicle.plate_number}'."
    return "Vehicle information updated successfully."


# ============================================================
# DELETE
# ============================================================


def delete_vehicle(plate_number):
    """Deletes a vehicle record by plate_number."""
    query = "DELETE FROM vehicles WHERE plate_number = ?"
    rows = execute_query(query, (plate_number,), fetch=False)
    st.cache_data.clear()
    if rows == 0:
        return f"No vehicle found with plate number '{plate_number}'."
    return "Vehicle deleted successfully."
