# Controller for vehicle registration operations
# Validates all inputs before delegating to the service layer
from models.registration_model import Registration
from services import registration_service
from db.query_helpers import (
    validate_not_empty,
    validate_in_set,
    validate_date_order,
    sanitize_string,
    to_date_string,
    VALID_REGISTRATION_STATUSES,
)


def _build_registration(data: dict) -> Registration:
    """
    Validates and constructs a Registration object from raw form data.
    Raises ValueError with a descriptive message on invalid input.
    """
    registration_number = sanitize_string(
        data.get("registration_number", ""), "Registration Number", min_len=1
    )
    plate_number = sanitize_string(data.get("plate_number", ""), "Plate Number", min_len=5)

    registration_status = sanitize_string(
        data.get("registration_status", ""), "Registration Status"
    )
    validate_in_set(registration_status, VALID_REGISTRATION_STATUSES, "Registration Status")

    reg_date = to_date_string(data.get("registration_date"), "Registration Date")
    exp_date = to_date_string(data.get("expiration_date"), "Expiration Date")
    validate_date_order(reg_date, exp_date, "Registration Date", "Expiration Date")

    return Registration(
        registration_number=registration_number,
        registration_date=reg_date,
        expiration_date=exp_date,
        registration_status=registration_status,
        plate_number=plate_number,
    )


# ============================================================
# CRUD Operations
# ============================================================

def create_vehicle_registration(data: dict) -> str:
    """Validates input and creates a new registration."""
    registration = _build_registration(data)
    return registration_service.register_new_vehicle_registration(registration)


def update_registration(data: dict) -> str:
    """Validates input and updates an existing registration."""
    registration = _build_registration(data)
    return registration_service.update_vehicle_registration(registration)


def delete_registration(registration_number: str) -> str:
    """Validates the registration number and deletes the record."""
    registration_number = sanitize_string(registration_number, "Registration Number")
    return registration_service.delete_vehicle_registration(registration_number)


# ============================================================
# Read / Report Operations
# ============================================================

def get_registrations_by_criteria(filters: dict) -> list:
    """Retrieves registrations matching user-selected filter criteria."""
    return registration_service.fetch_vehicle_registrations_by_criteria(
        registration_status=filters.get("registration_status", "ALL"),
        plate_number=filters.get("plate_number", "ALL"),
    )
